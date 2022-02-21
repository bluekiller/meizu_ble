import logging
from datetime import timedelta

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


async def async_setup_entry(hass, entry, async_add_entities):
    config = entry.data
    SENSOR_TYPES[SENSOR_TEMPERATURE][1] = hass.config.units.temperature_unit
    name = config[CONF_NAME]
    mac = config.get(CONF_MAC)
    client = MZBtIr(mac)

    # 定时更新
    async def update_interval():
        _LOGGER.debug("updating sensors [%s]", mac)
        client.update()

    coordinator = DataUpdateCoordinator(hass, _LOGGER,
                                        name=f'meizu_ble_mod[{mac}]',
                                        update_interval=timedelta(seconds=config.get(CONF_SCAN_INTERVAL)),
                                        update_method=update_interval)

    dev = [
        MeizuBLESensor(
            client,
            SENSOR_TEMPERATURE,
            SENSOR_TYPES[SENSOR_TEMPERATURE][1],
            name,
            coordinator,
        ),
        MeizuBLESensor(
            client,
            SENSOR_HUMIDITY,
            SENSOR_TYPES[SENSOR_HUMIDITY][1],
            name,
            coordinator,
        ),
        MeizuBLESensor(
            client,
            SENSOR_BATTERY,
            SENSOR_TYPES[SENSOR_BATTERY][1],
            name,
            coordinator,
        )
    ]

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(dev)


class MeizuBLESensor(CoordinatorEntity, SensorEntity):
    """Implementation of the DHT sensor."""

    def __init__(
            self,
            client,
            sensor_type,
            temp_unit,
            name,
            coordinator
    ):
        """Initialize the sensor."""
        CoordinatorEntity.__init__(self, coordinator)
        self.client_name = name
        self._name = SENSOR_TYPES[sensor_type][0]
        self.client = client
        self.temp_unit = temp_unit
        self.type = sensor_type
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._attr_device_class = SENSOR_TYPES[sensor_type][2]
        self._attributes = {}

    @property
    def unique_id(self):
        return f"{self.client._mac}{self.type}"

    @property
    def device_info(self):
        mac = self.client._mac
        return {
            "configuration_url": "https://github.com/bluekiller/meizu_ble_mod",
            "identifiers": {
                (DOMAIN, mac)
            },
            "name": self.client_name,
            "manufacturer": "Meizu",
            "model": mac,
            "sw_version": VERSION,
            "via_device": (DOMAIN, mac),
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.client_name}{self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        state = 0
        # 显示数据
        if self.type == SENSOR_TEMPERATURE:
            state = self.client.temperature()
        elif self.type == SENSOR_HUMIDITY:
            state = self.client.humidity()
        elif self.type == SENSOR_BATTERY:
            state = self.client.battery()
        # 数据大于0，则更新
        if state > 0:
            self._state = state
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        if self.type == SENSOR_BATTERY:
            self._attributes.update({'voltage': self.client.voltage(), 'mac': self.client._mac})
        return self._attributes
