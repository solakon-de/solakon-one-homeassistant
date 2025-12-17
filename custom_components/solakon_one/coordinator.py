"""The Solakon ONE integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .modbus import SolakonModbusHub

_LOGGER = logging.getLogger(__name__)


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
