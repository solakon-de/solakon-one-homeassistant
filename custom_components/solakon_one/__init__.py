"""The Solakon ONE integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, PLATFORMS
from .modbus import SolakonModbusHub
from .utils import getModbusHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solakon ONE from a config entry."""
    hub = getModbusHub(hass, entry)

    await hub.async_setup()

    if not await hub.async_test_connection():
        raise ConfigEntryNotReady("Cannot connect to Solakon ONE device")

    coordinator = SolakonDataCoordinator(hass, hub)
    # Coordinator isn't tied to a config entry object, so call a regular refresh
    # rather than async_config_entry_first_refresh which is only supported
    # for coordinators that are created with a config entry.
    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "hub": hub,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hub = hass.data[DOMAIN][entry.entry_id]["hub"]
        await hub.async_close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class SolakonDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Solakon ONE."""

    def __init__(self, hass: HomeAssistant, hub: SolakonModbusHub) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Solakon ONE",
            update_interval=timedelta(seconds=hub.scan_interval),
        )
        self.hub = hub

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Solakon ONE."""
        try:
            data = await self.hub.async_read_all_data()
            if not data:
                raise UpdateFailed("Failed to fetch data from device")
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
