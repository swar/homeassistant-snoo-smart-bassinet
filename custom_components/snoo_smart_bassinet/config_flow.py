"""Adds config flow for SNOO Smart Bassinet."""

import logging
import voluptuous as vol

from .const import (
    DOMAIN,
    TITLE,
)
from homeassistant import config_entries
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_TOKEN,
)
from oauthlib.oauth2.rfc6749.errors import CustomOAuth2Error
from pysnoo import SnooAuthSession


_LOGGER = logging.getLogger(__name__)


async def _get_token(user_input):
    try:
        async with SnooAuthSession() as auth:
            token = await auth.fetch_token(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
    except CustomOAuth2Error:
        token = None
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
            self._data = user_input
            if CONF_TOKEN in user_input and len(user_input[CONF_TOKEN]) > 0:
                token = user_input[CONF_TOKEN]
            else:
                token = await _get_token(user_input)
            if token and len(self._errors) == 0:
                user_input[CONF_TOKEN] = token
                return self.async_create_entry(title=TITLE, data=user_input)
            else:
                self._errors['base'] = "failed_auth"
                return await self._show_config_form(user_input)

        self._errors = {}
        if not user_input:
            user_input = {}
        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit configuration data."""

        def _get_default(key, fallback_default="") -> None:
            """Gets default value for key."""
            return user_input.get(key, fallback_default)

        def _get_data_schema():
            return vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=_get_default(CONF_USERNAME)): str,
                    vol.Required(CONF_PASSWORD, default=_get_default(CONF_PASSWORD)): str,
                    vol.Optional(CONF_TOKEN, default=_get_default(CONF_TOKEN)): str,
                }
            )

        return self.async_show_form(step_id="user", data_schema=_get_data_schema(), errors=self._errors)
