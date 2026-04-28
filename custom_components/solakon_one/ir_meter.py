"""Solakon PowerTracker IR meter HTTP client."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .exceptions import CannotConnect

_LOGGER = logging.getLogger(__name__)

# Keys produced by this client and consumed by the coordinator/sensors.
DATA_GRID_POWER = "grid_power"
DATA_GRID_IMPORT_TOTAL = "grid_import_total"
DATA_GRID_EXPORT_TOTAL = "grid_export_total"

IR_METER_DATA_KEYS = (
    DATA_GRID_POWER,
    DATA_GRID_IMPORT_TOTAL,
    DATA_GRID_EXPORT_TOTAL,
)

# Possible JSON paths for energy totals returned by the device. The PowerTracker
# IR exposes the parsed SML values under the "extracted" object; the field name
# depends on firmware/meter, so we try a few common variants.
_IMPORT_KEYS = (
    "total_energy_in_wh",
    "energy_consumed_wh",
    "total_consumed_wh",
    "energy_in_wh",
)
_EXPORT_KEYS = (
    "total_energy_out_wh",
    "energy_delivered_wh",
    "total_delivered_wh",
    "energy_out_wh",
)


class SolakonIRMeterClient:
    """Async client for the Solakon PowerTracker IR local API."""

    def __init__(self, hass: HomeAssistant, host: str, *, timeout: float = 5.0) -> None:
        """Initialize the IR meter client."""
        self._hass = hass
        self._host = host.strip()
        self._timeout = ClientTimeout(total=timeout)
        self._session: ClientSession = async_get_clientsession(hass)

    @property
    def host(self) -> str:
        """Return the configured IR meter host."""
        return self._host

    @property
    def url(self) -> str:
        """Return the status endpoint URL."""
        host = self._host
        if "://" not in host:
            host = f"http://{host}"
        return f"{host.rstrip('/')}/api/v1/status"

    async def async_test_connection(self) -> bool:
        """Return True if the device responds with a parseable payload."""
        try:
            payload = await self._async_fetch()
        except CannotConnect:
            return False
        return self._extract_power(payload) is not None

    async def async_read_data(self) -> dict[str, Any]:
        """Fetch and normalize data from the IR meter."""
        payload = await self._async_fetch()

        data: dict[str, Any] = {}

        power = self._extract_power(payload)
        if power is not None:
            data[DATA_GRID_POWER] = power

        import_kwh = self._extract_energy_kwh(payload, _IMPORT_KEYS)
        if import_kwh is not None:
            data[DATA_GRID_IMPORT_TOTAL] = import_kwh

        export_kwh = self._extract_energy_kwh(payload, _EXPORT_KEYS)
        if export_kwh is not None:
            data[DATA_GRID_EXPORT_TOTAL] = export_kwh

        return data

    async def _async_fetch(self) -> dict[str, Any]:
        """Perform the HTTP GET and return the JSON body."""
        try:
            async with self._session.get(self.url, timeout=self._timeout) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except (ClientError, asyncio.TimeoutError, ValueError) as err:
            raise CannotConnect(f"IR meter request failed: {err}") from err

    @staticmethod
    def _extract_power(payload: dict[str, Any]) -> float | None:
        """Return instantaneous power in W, or None if not present."""
        extracted = payload.get("extracted") if isinstance(payload, dict) else None
        if isinstance(extracted, dict):
            value = extracted.get("instantaneous_power_w")
            if value is None:
                value = extracted.get("power_w")
            if value is not None:
                return _coerce_float(value)

        # Some firmwares put it at the top level.
        if isinstance(payload, dict):
            value = payload.get("instantaneous_power_w") or payload.get("power_w")
            if value is not None:
                return _coerce_float(value)

        return None

    @staticmethod
    def _extract_energy_kwh(
        payload: dict[str, Any], keys: tuple[str, ...]
    ) -> float | None:
        """Return cumulative energy in kWh from the first matching key."""
        sources: list[dict[str, Any]] = []
        if isinstance(payload, dict):
            extracted = payload.get("extracted")
            if isinstance(extracted, dict):
                sources.append(extracted)
            sources.append(payload)

        for source in sources:
            for key in keys:
                if key in source and source[key] is not None:
                    wh = _coerce_float(source[key])
                    if wh is None:
                        continue
                    if key.endswith("_kwh"):
                        return wh
                    return wh / 1000.0

            for key in keys:
                kwh_key = key.replace("_wh", "_kwh")
                if kwh_key != key and kwh_key in source and source[kwh_key] is not None:
                    return _coerce_float(source[kwh_key])

        return None


def _coerce_float(value: Any) -> float | None:
    """Best-effort float conversion."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
