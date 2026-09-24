"""Config flow for Solakon ONE integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, selector

from .const import (
    CONF_DEVICE_ID,
    DEFAULT_DEVICE_ID,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .exceptions import CannotConnect
from .modbus import get_modbus_hub

_LOGGER = logging.getLogger(__name__)


SCAN_INTERVAL_NUMBER_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        mode=selector.NumberSelectorMode.SLIDER,
        min=1,
        max=300,
        step=1,
        unit_of_measurement=UnitOfTime.SECONDS,
    ),
)

STEP_RECONFIGURE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): vol.All(
            selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX,
                    min=1,
                    max=247,
                    step=1,
                ),
            ),
            vol.Coerce(int),
        ),
    }
)

STEP_USER_DATA_SCHEMA = STEP_RECONFIGURE_DATA_SCHEMA.extend(
    {
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): SCAN_INTERVAL_NUMBER_SELECTOR,
    }
)

STEP_OPTIONS_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): SCAN_INTERVAL_NUMBER_SELECTOR,
    }
)


def build_unique_id(data: Mapping[str, Any]) -> str:
    """Build the unique ID identifying a device by its connection settings."""
    return (
        f"{data[CONF_HOST]}:{data[CONF_PORT]}:"
        f"{data.get(CONF_DEVICE_ID, DEFAULT_DEVICE_ID)}"
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    hub = get_modbus_hub(hass, data)

    await hub.async_setup()

    if not await hub.async_test_connection():
        await hub.async_close()
        raise CannotConnect("Cannot connect to device")

    try:
        info = await hub.async_get_device_info()
        await hub.async_close()
    except Exception as err:
        await hub.async_close()
        raise CannotConnect(f"Failed to get device info: {err}") from err

    return {"device_info": info}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for Solakon ONE."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(build_unique_id(user_input))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, user_input or {}
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the connection settings."""
        reconfigure_entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            # Aborts when another entry already uses these settings. The entry
            # being reconfigured is excluded from the check.
            self._async_abort_entries_match(
                {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_DEVICE_ID: user_input.get(CONF_DEVICE_ID, DEFAULT_DEVICE_ID),
                }
            )

            try:
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # The unique ID is derived from the connection settings, so it
                # has to follow them. Entities and the device keep their
                # identity because those are keyed on the entry ID.
                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    unique_id=build_unique_id(user_input),
                    data_updates=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            errors=errors,
            data_schema=self.add_suggested_values_to_schema(
                STEP_RECONFIGURE_DATA_SCHEMA, user_input or reconfigure_entry.data
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlowWithReload):
    """Handle options flow for Solakon ONE."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Do not set `self.config_entry` on the flow handler (deprecated).
        # Store as a private attribute instead.
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                STEP_OPTIONS_DATA_SCHEMA,
                self._config_entry.options or self._config_entry.data,
            ),
        )
