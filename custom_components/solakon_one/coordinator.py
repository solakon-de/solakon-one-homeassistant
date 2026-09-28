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
            self._compute_derived_values(data)
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    def _compute_derived_values(self, data: dict[str, Any]) -> None:
        """Compute derived sensor values from raw register data."""
        # System loss power (W): PV power + battery discharge power - AC output power
        # Note: raw battery_power is positive when charging, negative when discharging.
        pv_power = data.get("total_pv_power")
        battery_power_raw = data.get("battery_power")
        ac_power = data.get("active_power")
        if (
            pv_power is not None
            and battery_power_raw is not None
            and ac_power is not None
        ):
            losses_w = pv_power - battery_power_raw - ac_power
            data["system_loss_power"] = max(0, round(losses_w))

        # System loss energy (kWh): (PV energy + battery discharge) - (grid export + battery charge)
        pv_energy = data.get("pv_total_energy")
        batt_discharge = data.get("battery_total_discharge_energy")
        grid_export = data.get("grid_total_export_energy")
        batt_charge = data.get("battery_total_charge_energy")
        if (
            pv_energy is not None
            and batt_discharge is not None
            and grid_export is not None
            and batt_charge is not None
        ):
            losses_kwh = (pv_energy + batt_discharge) - (grid_export + batt_charge)
            data["system_loss_energy"] = round(max(0.0, losses_kwh), 2)
