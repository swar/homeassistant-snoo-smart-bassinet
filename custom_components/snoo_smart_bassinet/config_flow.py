"""Adds config flow for SNOO Smart Bassinet."""

import logging
import voluptuous as vol

from const import (
    DOMAIN,
    TITLE,
)
from homeassistant import config_entries
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_TOKEN,
)
from pysnoo import SnooAuthSession


_LOGGER = logging.getLogger(__name__)


def _get_token(user_input):
    async with SnooAuthSession() as auth:
        token = await auth.fetch_token(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
    return token


@config_entries.HANDLERS.register(DOMAIN)
class SNOOSmartBassinetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for SNOO Smart Bassinet."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self._data = {}
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            if CONF_TOKEN not in user_input:
                token = await _get_token(user_input)
            else:
                token = user_input[CONF_TOKEN]
            if token and len(self._errors) == 0:
                user_input[CONF_TOKEN] = token
                return self.async_create_entry(title=TITLE, data=user_input)
            # TODO: Add error handling

        self._errors = {}
        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit configuration data."""

        def _get_default(key, fallback_default=None) -> None:
            """Gets default value for key."""
            return user_input.get(key, self._data.get(key, fallback_default))

        def _get_data_scheme():
            return vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=_get_default(CONF_USERNAME)): str,
                    vol.Required(CONF_PASSWORD, default=_get_default(CONF_PASSWORD)): str,
                    vol.Optional(CONF_TOKEN, default=_get_default(CONF_TOKEN)): str,
                }
            )

        return self.async_show_form(step_id="init", data_scheme=_get_data_scheme(), errors=self._errors)
