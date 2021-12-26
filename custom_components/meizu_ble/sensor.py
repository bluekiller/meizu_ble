from datetime import timedelta
import logging, asyncio

import voluptuous as vol

from homeassistant.helpers.event import async_track_time_interval
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
import homeassistant.helpers.config_validation as cv

from .meizu import MZBtIr
from .const import DOMAIN, VERSION

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

    dev = [
        MeizuBLESensor(
                    client,
                    SENSOR_TEMPERATURE,
                    SENSOR_TYPES[SENSOR_TEMPERATURE][1],
                    name,
                ),
        MeizuBLESensor(
                    client,
                    SENSOR_HUMIDITY,
                    SENSOR_TYPES[SENSOR_HUMIDITY][1],
                    name,
                ),
        MeizuBLESensor(
                    client,
                    SENSOR_BATTERY,
                    SENSOR_TYPES[SENSOR_BATTERY][1],
                    name,
                )
    ]

    async_add_entities(dev, True)

    # 定时更新
    async def update_interval(now):
        client.update()
        task = []
        for ble in dev:
            task.append(ble.async_update())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(task))
        loop.close()

    async_track_time_interval(hass, update_interval, timedelta(seconds=config.get(CONF_SCAN_INTERVAL)))

class MeizuBLESensor(SensorEntity):
    """Implementation of the DHT sensor."""

    def __init__(
        self,
        client,
        sensor_type,
        temp_unit,
        name,
    ):
        """Initialize the sensor."""
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
            "configuration_url": "https://github.com/shaonianzhentan/meizu_ble",
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
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        state = 0
        # 显示数据
        if self.type == SENSOR_TEMPERATURE:
            state = self.client.temperature()
        elif self.type == SENSOR_HUMIDITY:
            state = self.client.humidity()
        elif self.type == SENSOR_BATTERY:
            state = self.client.battery()
            self._attributes.update({ 'voltage': self.client.voltage(), 'mac': self.client._mac })
        # 数据大于0，则更新
        if state > 0:
            self._state = state