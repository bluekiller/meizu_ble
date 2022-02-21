from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_NAME, SCAN_INTERVAL

DATA_SCHEMA = vol.Schema({
    vol.Required("name", default=DEFAULT_NAME): str,
    vol.Required("mac"): str,
    vol.Required("scan_interval", default=SCAN_INTERVAL): int
})


class SimpleConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
        user_input['mac'] = user_input['mac'].upper()
        return self.async_create_entry(title=user_input['name'], data=user_input)
