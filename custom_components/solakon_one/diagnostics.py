"""Diagnostics support for Solakon ONE."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    return {
        "entry": config_entry.as_dict(),
        "data": coordinator.data,
    }
