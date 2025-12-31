"""IR Meter HTTP client for Solakon IR Meter integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

# OBIS code mappings for common meter values
OBIS_MAPPINGS = {
    "1-0:1.7.0": "active_power",  # Instantaneous active power (kW)
    "1-0:1.8.0": "total_energy",  # Total energy (kWh)
    "1-0:1.8.1": "total_energy_tariff1",  # Total energy tariff 1 (kWh)
    "1-0:1.8.2": "total_energy_tariff2",  # Total energy tariff 2 (kWh)
    "1-0:32.7.0": "voltage_l1",  # Voltage L1 (V)
    "1-0:52.7.0": "voltage_l2",  # Voltage L2 (V)
    "1-0:72.7.0": "voltage_l3",  # Voltage L3 (V)
    "1-0:31.7.0": "current_l1",  # Current L1 (A)
    "1-0:51.7.0": "current_l2",  # Current L2 (A)
    "1-0:71.7.0": "current_l3",  # Current L3 (A)
    "1-0:13.7.0": "power_factor",  # Power factor
    "1-0:0.0.0": "meter_serial",  # Meter serial number
    "1-0:0.2.0": "meter_version",  # Meter firmware version
}


class IRMeterHub:
    """Hub for communicating with Solakon IR Meter via HTTP API."""

    def __init__(
        self,
        host: str,
        port: int = 80,
        scan_interval: int = 30,
    ) -> None:
        """Initialize the IR Meter hub."""
        self._host = host
        self._port = port
        self.scan_interval = scan_interval
        self._base_url = f"http://{host}:{port}"
        self._session: aiohttp.ClientSession | None = None
        self._lock = asyncio.Lock()

    async def async_setup(self) -> None:
        """Set up the HTTP session."""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(timeout=timeout)

    async def async_close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def async_test_connection(self) -> bool:
        """Test connection to the IR Meter."""
        try:
            data = await self._async_fetch_status()
            return data is not None and "device" in data
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False

    async def async_get_device_info(self) -> dict[str, Any]:
        """Get device information from IR Meter."""
        data = await self._async_fetch_status()
        if not data or "device" not in data:
            return {}

        device = data.get("device", {})
        meter = data.get("meter", {})

        return {
            "manufacturer": "Solakon",
            "model": f"IR Meter {device.get('hw', 'Unknown')}",
            "serial_number": device.get("hw_sn", ""),
            "version": device.get("fw_ver", ""),
            "hw_revision": device.get("hw_rev", ""),
            "meter_protocol": meter.get("serial_protocol", ""),
            "meter_manufacturer": meter.get("manufacturer_code", ""),
            "meter_model": meter.get("device_identification", ""),
        }

    async def async_read_all_data(self) -> dict[str, Any]:
        """Read all data from IR Meter API."""
        data = await self._async_fetch_status()
        if not data:
            return {}

        result: dict[str, Any] = {}

        # Device information
        device = data.get("device", {})
        result["uptime"] = device.get("uptime")
        result["firmware_version"] = device.get("fw_ver")

        # WiFi information
        wifi = data.get("wifi", {})
        result["wifi_rssi"] = wifi.get("rssi")
        result["wifi_ssid"] = wifi.get("ssid")
        result["wifi_channel"] = wifi.get("channel")
        result["ip_address"] = wifi.get("ip")

        # Extracted values (pre-calculated by the device)
        extracted = data.get("extracted", {})
        result["instantaneous_power"] = extracted.get("instantaneous_power_w")
        result["energy_total"] = extracted.get("energy_summation_kwh")

        # Parse OBIS values
        meter = data.get("meter", {})
        obis_values = meter.get("obis_values", [])

        for obis in obis_values:
            code = obis.get("obis_code", "")
            value_str = obis.get("value", "")
            unit = obis.get("unit", "")

            # Map OBIS code to friendly name
            if code in OBIS_MAPPINGS:
                key = OBIS_MAPPINGS[code]
                # Convert value to appropriate type
                value = self._parse_obis_value(value_str, unit)
                result[key] = value

            # Store raw OBIS values with code as key for completeness
            safe_code = code.replace(":", "_").replace("-", "_").replace(".", "_")
            result[f"obis_{safe_code}"] = value_str

        # Meter identification
        result["meter_protocol"] = meter.get("serial_protocol")
        result["meter_manufacturer"] = meter.get("manufacturer_code")
        result["meter_identification"] = meter.get("device_identification")

        return result

    def _parse_obis_value(self, value_str: str, unit: str) -> float | str | None:
        """Parse OBIS value string to appropriate type."""
        if not value_str:
            return None

        try:
            # Try to parse as float for numeric values
            return float(value_str)
        except ValueError:
            # Return as string for non-numeric values
            return value_str

    async def _async_fetch_status(self) -> dict[str, Any] | None:
        """Fetch status from IR Meter API."""
        if not self._session:
            await self.async_setup()

        url = f"{self._base_url}/api/v1/status"

        async with self._lock:
            try:
                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Failed to fetch IR Meter status: HTTP %s",
                            response.status,
                        )
                        return None

                    return await response.json()

            except aiohttp.ClientError as err:
                _LOGGER.error("HTTP error fetching IR Meter status: %s", err)
                return None
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout fetching IR Meter status")
                return None
            except Exception as err:
                _LOGGER.error("Error fetching IR Meter status: %s", err)
                return None


def get_ir_meter_hub(data: dict[str, Any]) -> IRMeterHub:
    """Create an IR Meter hub from config data."""
    from .const import DEFAULT_IR_METER_PORT, DEFAULT_SCAN_INTERVAL
    from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

    return IRMeterHub(
        host=data[CONF_HOST],
        port=data.get(CONF_PORT, DEFAULT_IR_METER_PORT),
        scan_interval=data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
