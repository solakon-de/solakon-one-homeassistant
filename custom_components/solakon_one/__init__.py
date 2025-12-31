"""The Solakon ONE integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_DEVICE_TYPE,
    DEVICE_TYPE_IR_METER,
    DEVICE_TYPE_SOLAKON_ONE,
    PLATFORMS_IR_METER,
    PLATFORMS_SOLAKON_ONE,
)
from .coordinator import IRMeterDataCoordinator, SolakonDataCoordinator
from .ir_meter import get_ir_meter_hub
from .modbus import get_modbus_hub
from .types import IRMeterData, SolakonData

_LOGGER = logging.getLogger(__name__)


def _get_device_type(entry: ConfigEntry) -> str:
    """Get the device type from config entry."""
    # Check options first, then data for backwards compatibility
    device_type = entry.options.get(CONF_DEVICE_TYPE) or entry.data.get(CONF_DEVICE_TYPE)
    # Default to Solakon ONE for backwards compatibility with existing entries
    return device_type or DEVICE_TYPE_SOLAKON_ONE


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry[Any]) -> bool:
    """Set up Solakon device from a config entry."""
    device_type = _get_device_type(entry)

    if device_type == DEVICE_TYPE_IR_METER:
        return await _async_setup_ir_meter_entry(hass, entry)
    return await _async_setup_solakon_one_entry(hass, entry)


async def _async_setup_solakon_one_entry(hass: HomeAssistant, entry: ConfigEntry[SolakonData]) -> bool:
    """Set up Solakon ONE from a config entry."""
    hub = get_modbus_hub(hass, entry.options | entry.data)

    try:
        await hub.async_setup()

        if not await hub.async_test_connection():
            raise ConfigEntryNotReady("Cannot connect to Solakon ONE device")
    except Exception as err:
        raise ConfigEntryNotReady(err) from err

    coordinator = SolakonDataCoordinator(hass, hub)
    await coordinator.async_refresh()

    entry.runtime_data = SolakonData(hub=hub, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_SOLAKON_ONE)

    return True


async def _async_setup_ir_meter_entry(hass: HomeAssistant, entry: ConfigEntry[IRMeterData]) -> bool:
    """Set up Solakon IR Meter from a config entry."""
    hub = get_ir_meter_hub(entry.options | entry.data)

    try:
        await hub.async_setup()

        if not await hub.async_test_connection():
            raise ConfigEntryNotReady("Cannot connect to Solakon IR Meter")
    except Exception as err:
        raise ConfigEntryNotReady(err) from err

    coordinator = IRMeterDataCoordinator(hass, hub)
    await coordinator.async_refresh()

    entry.runtime_data = IRMeterData(hub=hub, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_IR_METER)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry[Any]) -> bool:
    """Unload a config entry."""
    device_type = _get_device_type(entry)

    if device_type == DEVICE_TYPE_IR_METER:
        platforms = PLATFORMS_IR_METER
    else:
        platforms = PLATFORMS_SOLAKON_ONE

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, platforms):
        await entry.runtime_data.hub.async_close()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry[Any]) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
