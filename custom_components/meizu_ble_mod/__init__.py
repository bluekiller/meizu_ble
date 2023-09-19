import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, PLATFORMS
from .meizu import MZBtIr

CONFIG_SCHEMA = cv.deprecated(DOMAIN)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    config = entry.data
    mac = config.get(CONF_MAC)
    ble_device = bluetooth.async_ble_device_from_address(hass, mac, connectable=True)
    if not ble_device:
        _LOGGER.info("device[%s] is not found", mac)
    client = MZBtIr(ble_device)
    hass.data.setdefault(DOMAIN, {})[mac] = client
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = hass.data[DOMAIN].get(entry.data.get(CONF_MAC))
    if client:
        await client.close()
    return await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
