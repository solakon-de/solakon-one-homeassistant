"""The Solakon ONE integration."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import PLATFORMS, SCAN_INTERVAL
from .coordinator import SolakonDataCoordinator
from .modbus import SolakonModbusHub
from .types import SolakonConfigEntry, SolakonData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: SolakonConfigEntry) -> bool:
    """Set up Solakon ONE from a config entry."""
    hub = SolakonModbusHub(
        hass,
        entry.data["host"],
        entry.data["port"],
        entry.data.get("slave_id", 1),
        entry.data.get("scan_interval", SCAN_INTERVAL),
    )

    await hub.async_setup()

    if not await hub.async_test_connection():
        raise ConfigEntryNotReady("Cannot connect to Solakon ONE device")

    coordinator = SolakonDataCoordinator(hass, hub)
    # Coordinator isn't tied to a config entry object, so call a regular refresh
    # rather than async_config_entry_first_refresh which is only supported
    # for coordinators that are created with a config entry.
    await coordinator.async_refresh()

    entry.runtime_data = SolakonData(hub=hub, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: SolakonConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hub = entry.runtime_data.hub
        await hub.async_close()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: SolakonConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

