import time, asyncio
import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.util.dt import utcnow
from .shaonianzhentan import save_yaml, load_yaml
from .meizu import MZBtIr

from homeassistant.components.remote import (
    PLATFORM_SCHEMA,
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    RemoteEntity,
)

from homeassistant.const import CONF_NAME, CONF_MAC
import homeassistant.helpers.config_validation as cv

DEFAULT_NAME = "魅族智能遥控器"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):

    name = config.get(CONF_NAME)
    mac = config.get(CONF_MAC)
    add_entities([MeizuRemote(mac, name, hass)])

class MeizuRemote(RemoteEntity):

    def __init__(self, mac, name, hass):
        self.hass = hass
        self._mac = mac
        self._name = name
        self.config_file = hass.config.path("custom_components/meizu_ble/ir.yaml")
        self.ble = MZBtIr(mac)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._mac

    @property
    def is_on(self):
        return True

    @property
    def should_poll(self):
        return False

    async def async_turn_on(self, activity: str = None, **kwargs):
         """Turn the remote on."""

    async def async_turn_off(self, activity: str = None, **kwargs):
         """Turn the remote off."""
         
    async def async_send_command(self, command, **kwargs):
        device = kwargs.get('device', '')
        if device == '':
            return
        key = command[0]
        # 读取配置文件
        command_list = load_yaml(self.config_file)
        dev = command_list.get(device, {})
        # 判断配置是否存在
        if key in dev:
            ir = dev[key].strip()
            arr = ir.split(':')
            self.ble.sendIr(arr[0], arr[1])

    async def async_learn_command(self, **kwargs):
        command = kwargs.get('command', '')