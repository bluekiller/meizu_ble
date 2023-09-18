"""Meizu BLE Sensors"""
import logging
from datetime import timedelta

import homeassistant.components.bluetooth
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_MAC,
    CONF_SCAN_INTERVAL,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_BATTERY,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN, VERSION
from .meizu import MZBtIr

_LOGGER = logging.getLogger(__name__)

SENSOR_TEMPERATURE = "temperature"
SENSOR_HUMIDITY = "humidity"
SENSOR_BATTERY = "battery"

SENSOR_TYPES = {
    SENSOR_TEMPERATURE: ["温度", None, DEVICE_CLASS_TEMPERATURE],
    SENSOR_HUMIDITY: ["湿度", PERCENTAGE, DEVICE_CLASS_HUMIDITY],
    SENSOR_BATTERY: ["电量", PERCENTAGE, DEVICE_CLASS_BATTERY],
}


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Setup meizu ble sensor entry"""
    config = entry.data
    SENSOR_TYPES[SENSOR_TEMPERATURE][1] = hass.config.units.temperature_unit
    name = config[CONF_NAME]
    mac = config.get(CONF_MAC)
    client = MZBtIr(homeassistant.components.bluetooth.async_ble_device_from_address(hass, mac, connectable=True))
    hass.data[DOMAIN][mac] = client
    coordinator = SensorCoordinator(hass, client, config)
    dev = [
        MeizuBLESensor(
            client,
            SENSOR_TEMPERATURE,
            name,
            coordinator,
        ),
        MeizuBLESensor(
            client,
            SENSOR_HUMIDITY,
            name,
            coordinator,
        ),
        MeizuBLESensor(
            client,
            SENSOR_BATTERY,
            name,
            coordinator,
        )
    ]

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(dev)


async def async_unload_entry(hass, entry):
    client = hass.data[DOMAIN].get(entry.data.get(CONF_MAC))
    if client:
        await client.close()


class SensorCoordinator(DataUpdateCoordinator):
    """Coordinator of sensors"""

    def __init__(self, hass, client: MZBtIr, config):
        super().__init__(hass, _LOGGER, name=f'meizu_ble_mod[{client.mac()}]',
                         update_interval=timedelta(seconds=config.get(CONF_SCAN_INTERVAL)))
        self._client = client
        self._seq = 0

    async def _async_update_data(self):
        _LOGGER.debug("updating sensors [%s]", self._client.mac())
        self._client.update(self._seq == 0)
        if self._seq >= 10:
            self._seq = 0
        else:
            self._seq += 1


class MeizuBLESensor(CoordinatorEntity, SensorEntity):
    """Implementation of the DHT sensor."""

    def __init__(
            self,
            client: MZBtIr,
            sensor_type,
            name,
            coordinator
    ):
        """Initialize the sensor."""
        CoordinatorEntity.__init__(self, coordinator)
        self._client_name = name
        self._name = SENSOR_TYPES[sensor_type][0]
        self._client = client
        self._type = sensor_type
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._attr_device_class = SENSOR_TYPES[sensor_type][2]
        self._attributes = {}

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._client.mac()}{self._type}"

    @property
    def device_info(self):
        """Return device specific attributes."""
        mac = self._client.mac()
        return {
            "configuration_url": "https://github.com/bluekiller/meizu_ble_mod",
            "identifiers": {
                (DOMAIN, mac)
            },
            "name": self._client_name,
            "manufacturer": "Meizu",
            "model": mac,
            "sw_version": VERSION,
            "via_device": (DOMAIN, mac),
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._client_name}{self._name}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self._type == SENSOR_TEMPERATURE:
            self._state = self._client.temperature()
        elif self._type == SENSOR_HUMIDITY:
            self._state = self._client.humidity()
        elif self._type == SENSOR_BATTERY:
            self._state = self._client.battery()

        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        if self._type == SENSOR_BATTERY:
            self._attributes.update({'voltage': self._client.voltage(), 'mac': self._client.mac()})
        return self._attributes
