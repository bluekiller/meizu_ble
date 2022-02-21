import logging

from homeassistant.components.remote import (
    RemoteEntity,
)
from homeassistant.const import CONF_NAME, CONF_MAC

from .const import DOMAIN, VERSION
from .meizu import MZBtIr
from .shaonianzhentan import load_yaml

DEFAULT_NAME = "魅族智能遥控器"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    config = entry.data
    name = config.get(CONF_NAME)
    mac = config.get(CONF_MAC)
    async_add_entities([MeizuRemote(mac, name, hass)], True)


class MeizuRemote(RemoteEntity):

    def __init__(self, mac, name, hass):
        self.hass = hass
        self._mac = mac
        self._name = name
        self.config_file = hass.config.path("custom_components/meizu_ble_mod/ir.yaml")
        self.ble = MZBtIr(mac)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._mac

    @property
    def device_info(self):
        mac = self._mac
        return {
            "configuration_url": "https://github.com/bluekiller/meizu_ble_mod",
            "identifiers": {
                (DOMAIN, mac)
            },
            "name": self._name,
            "manufacturer": "Meizu",
            "model": mac,
            "sw_version": VERSION,
            "via_device": (DOMAIN, mac),
        }

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
        if device != '':
            dev = command_list.get(device, {})
            # 判断配置是否存在
            if key in dev:
                ir_command = dev[key]
            else:
                ir_command = key
            self.ble.send_ir_raw(ir_command)
            return

    async def async_learn_command(self, **kwargs):
        print('未测试通过')
        # try:
        #     data = self.ble.receiveIr()
        #     bb = bytes(data)
        #     self.hass.components.persistent_notification.async_create(f'''
        #         收到的红外码是：{bb.hex()}
        #         建议共享到公共库：https://github.com/shaonianzhentan/meizu_ble/issues/1
        #     ''', title="魅族智能遥控器")
        # except Exception as ex:
        #     self.hass.components.persistent_notification.async_create(f"录码失败，请隔近一点再试试", title="魅族智能遥控器")
