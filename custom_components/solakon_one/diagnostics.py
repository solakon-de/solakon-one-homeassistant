"""Diagnostics support for Solakon ONE."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    _: HomeAssistant,
    config_entry: ConfigEntry[Any]
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    coordinator = config_entry.runtime_data.coordinator

    return {
        "entry": config_entry.as_dict(),
        "data": coordinator.data,
    }
