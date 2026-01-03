"""Config flow for Solakon ONE integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, selector

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_TYPE,
    DEFAULT_DEVICE_ID,
    DEFAULT_IR_METER_PORT,
    DEFAULT_NAME,
    DEFAULT_NAME_IR_METER,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_TYPE_IR_METER,
    DEVICE_TYPE_SOLAKON_ONE,
    DOMAIN,
)
from .ir_meter import get_ir_meter_hub
from .modbus import get_modbus_hub

_LOGGER = logging.getLogger(__name__)


SCAN_INTERVAL_NUMBER_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        mode=selector.NumberSelectorMode.SLIDER,
        min=1, max=300, step=1,
        unit_of_measurement=UnitOfTime.SECONDS,
    ),
)

# Device type selection schema
STEP_DEVICE_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_TYPE, default=DEVICE_TYPE_SOLAKON_ONE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value=DEVICE_TYPE_SOLAKON_ONE, label="Solakon ONE (Inverter)"),
                    selector.SelectOptionDict(value=DEVICE_TYPE_IR_METER, label="Solakon IR Meter"),
                ],
                mode=selector.SelectSelectorMode.LIST,
            ),
        ),
    }
)

# Solakon ONE (Modbus) configuration schema
STEP_SOLAKON_ONE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): vol.All(
            selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX,
                    min=1, max=247, step=1,
                ),
            ),
            vol.Coerce(int),
        ),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): SCAN_INTERVAL_NUMBER_SELECTOR,
    }
)

# IR Meter (HTTP API) configuration schema
STEP_IR_METER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_IR_METER_PORT): cv.port,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): SCAN_INTERVAL_NUMBER_SELECTOR,
    }
)

# Legacy schema for backwards compatibility
STEP_USER_DATA_SCHEMA = STEP_SOLAKON_ONE_DATA_SCHEMA

STEP_OPTIONS_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): SCAN_INTERVAL_NUMBER_SELECTOR,
    }
)


async def validate_solakon_one_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the Solakon ONE user input allows us to connect."""
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


async def validate_ir_meter_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the IR Meter user input allows us to connect."""
    hub = get_ir_meter_hub(data)

    await hub.async_setup()

    if not await hub.async_test_connection():
        await hub.async_close()
        raise CannotConnect("Cannot connect to IR Meter")

    try:
        info = await hub.async_get_device_info()
        await hub.async_close()
    except Exception as err:
        await hub.async_close()
        raise CannotConnect(f"Failed to get IR Meter info: {err}") from err

    return {"device_info": info}


# Legacy function for backwards compatibility
async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    return await validate_solakon_one_input(hass, data)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solakon ONE."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize config flow."""
        self._device_type: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the device type selection step."""
        if user_input is not None:
            self._device_type = user_input[CONF_DEVICE_TYPE]
            if self._device_type == DEVICE_TYPE_IR_METER:
                return await self.async_step_ir_meter()
            return await self.async_step_solakon_one()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_DEVICE_TYPE_SCHEMA,
        )

    async def async_step_solakon_one(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Solakon ONE configuration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_solakon_one_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input.get(CONF_DEVICE_ID, DEFAULT_DEVICE_ID)}"
                )
                self._abort_if_unique_id_configured()
                # Add device type to data
                user_input[CONF_DEVICE_TYPE] = DEVICE_TYPE_SOLAKON_ONE
                return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        return self.async_show_form(
            step_id="solakon_one",
            errors=errors,
            data_schema=self.add_suggested_values_to_schema(
                STEP_SOLAKON_ONE_DATA_SCHEMA,
                user_input or {}
            ),
        )

    async def async_step_ir_meter(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle IR Meter configuration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_ir_meter_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"ir_meter_{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()
                # Add device type to data
                user_input[CONF_DEVICE_TYPE] = DEVICE_TYPE_IR_METER
                return self.async_create_entry(title=DEFAULT_NAME_IR_METER, data=user_input)

        return self.async_show_form(
            step_id="ir_meter",
            errors=errors,
            data_schema=self.add_suggested_values_to_schema(
                STEP_IR_METER_DATA_SCHEMA,
                user_input or {}
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
    ) -> FlowResult:
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
