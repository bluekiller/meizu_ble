from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    PERCENTAGE,
)
import homeassistant.helpers.config_validation as cv

from .meizu import MZBtIr

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "魅族传感器"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

SENSOR_TEMPERATURE = "temperature"
SENSOR_HUMIDITY = "humidity"
SENSOR_TYPES = {
    SENSOR_TEMPERATURE: ["Temperature", None, DEVICE_CLASS_TEMPERATURE],
    SENSOR_HUMIDITY: ["Humidity", PERCENTAGE, DEVICE_CLASS_HUMIDITY],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    
    SENSOR_TYPES[SENSOR_TEMPERATURE][1] = hass.config.units.temperature_unit
    name = config[CONF_NAME]

    data = MZBtIr('68:3E:34:CC:E0:67')
    dev = [
        MeizuBLESensor(
                    data,
                    SENSOR_TEMPERATURE,
                    SENSOR_TYPES[SENSOR_TEMPERATURE][1],
                    name,
                ),
        MeizuBLESensor(
                    data,
                    SENSOR_HUMIDITY,
                    SENSOR_TYPES[SENSOR_HUMIDITY][1],
                    name,
                )
    ]

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
    def name(self):
        """Return the name of the sensor."""
        return f"{self.client_name} {self._name}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def update(self):
        """Get the latest data from the DHT and updates the states."""
        self.client.update()
        # 显示数据
        if self.type == SENSOR_TEMPERATURE:
            self._state = self.client.temperature()
        elif self.type == SENSOR_HUMIDITY:
            self._state = self.client.humidity()