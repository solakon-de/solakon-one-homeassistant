"""The Solakon ONE integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .exceptions import CannotConnect
from .ir_meter import SolakonIRMeterClient
from .modbus import SolakonModbusHub

_LOGGER = logging.getLogger(__name__)


class SolakonDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Solakon ONE."""

    def __init__(
        self,
        hass: HomeAssistant,
        hub: SolakonModbusHub,
        ir_meter: SolakonIRMeterClient | None = None,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Solakon ONE",
            update_interval=timedelta(seconds=hub.scan_interval),
        )
        self.hub = hub
        self.ir_meter = ir_meter

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Solakon ONE."""
        try:
            modbus_task = self.hub.async_read_all_data()
            if self.ir_meter is not None:
                ir_task = self.ir_meter.async_read_data()
                modbus_data, ir_data = await asyncio.gather(
                    modbus_task, ir_task, return_exceptions=True
                )
            else:
                modbus_data = await modbus_task
                ir_data = None

            if isinstance(modbus_data, Exception):
                raise UpdateFailed(
                    f"Error communicating with device: {modbus_data}"
                ) from modbus_data
            if not modbus_data:
                raise UpdateFailed("Failed to fetch data from device")

            data: dict[str, Any] = dict(modbus_data)

            if isinstance(ir_data, dict):
                data.update(ir_data)
            elif isinstance(ir_data, CannotConnect):
                _LOGGER.debug("IR meter read failed: %s", ir_data)
            elif isinstance(ir_data, Exception):
                _LOGGER.warning("Unexpected IR meter error: %s", ir_data)

            return data
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
