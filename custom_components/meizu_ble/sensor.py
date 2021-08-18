from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.helpers.event import track_time_interval, async_call_later
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_MAC,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_BATTERY,
    PERCENTAGE,
)
import homeassistant.helpers.config_validation as cv

from .meizu import MZBtIr

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "魅族智能遥控器"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

SENSOR_TEMPERATURE = "temperature"
SENSOR_HUMIDITY = "humidity"
SENSOR_BATTERY = "battery"

SENSOR_TYPES = {
    SENSOR_TEMPERATURE: ["温度", None, DEVICE_CLASS_TEMPERATURE],
    SENSOR_HUMIDITY: ["湿度", PERCENTAGE, DEVICE_CLASS_HUMIDITY],
    SENSOR_BATTERY: ["电量", PERCENTAGE, DEVICE_CLASS_BATTERY],    
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    
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

    # 定时更新
    def interval(now):
        client.update()
        for ble in dev:
            ble.update()

    track_time_interval(hass, interval, MIN_TIME_BETWEEN_UPDATES)

    add_entities(dev, True)


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

    @property
    def unique_id(self):
        return f"{self.client._mac}{self.type}"

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

    def update(self):
        # 显示数据
        if self.type == SENSOR_TEMPERATURE:
            self._state = self.client.temperature()
        elif self.type == SENSOR_HUMIDITY:
            self._state = self.client.humidity()
        elif self.type == SENSOR_BATTERY:
            self._state = self.client.battery()

    @property
    def device_info(self):
        model = 'Meizu'
        return {
            "identifiers": {
                (model, self.unique_id)
            },
            "name": "魅族智能遥控器",
            "manufacturer": "魅族",
            "model": model,
            "sw_version": "1.0",
            "via_device": (model, self.unique_id),
        }