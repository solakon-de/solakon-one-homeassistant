"""Modbus communication for Solakon ONE."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from bitflags import BitFlags
from pymodbus.client import AsyncModbusTcpClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DEVICE_ID,
    DEFAULT_DEVICE_ID,
    DEFAULT_MANUFACTURER,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    REGISTERS,
)
from .exceptions import CannotConnect

_LOGGER = logging.getLogger(__name__)

# Maximum number of registers that can be read in a single Modbus request
_MAX_BATCH_SIZE = 125
# Maximum gap between registers before starting a new batch
_BATCH_GAP_THRESHOLD = 10


def compute_register_batches(
    registers: dict[str, dict[str, Any]],
    static: bool = False,
) -> list[dict[str, Any]]:
    """Compute optimized batches of contiguous register reads.

    Groups registers that are close together (within _BATCH_GAP_THRESHOLD)
    into single Modbus read operations to minimize round-trips.

    Args:
        registers: The REGISTERS dict from const.py.
        static: If True, only include registers with "static": True.
                If False, only include registers without "static": True.

    Returns a list of batch descriptors:
        [
            {
                "address": start_address,
                "count": total_registers_to_read,
                "keys": [(key, offset, count, config), ...]
            },
            ...
        ]
    """
    # Filter and collect entries with their address info
    entries: list[tuple[str, dict[str, Any]]] = []
    for key, config in registers.items():
        is_static = config.get("static", False)
        if is_static == static:
            entries.append((key, config))

    if not entries:
        return []

    # Sort by address, then by key name for deterministic ordering
    entries.sort(key=lambda e: (e[1]["address"], e[0]))

    batches: list[dict[str, Any]] = []
    batch_start = entries[0][1]["address"]
    batch_end = batch_start + entries[0][1].get("count", 1)
    batch_keys: list[tuple[str, int, int, dict[str, Any]]] = [
        (entries[0][0], 0, entries[0][1].get("count", 1), entries[0][1])
    ]

    for key, config in entries[1:]:
        addr = config["address"]
        count = config.get("count", 1)
        entry_end = addr + count

        # Check if this entry fits in the current batch
        gap = addr - batch_end
        new_total = entry_end - batch_start

        if gap <= _BATCH_GAP_THRESHOLD and new_total <= _MAX_BATCH_SIZE:
            # Extend the batch
            offset = addr - batch_start
            batch_keys.append((key, offset, count, config))
            if entry_end > batch_end:
                batch_end = entry_end
        else:
            # Finalize current batch and start a new one
            batches.append({
                "address": batch_start,
                "count": batch_end - batch_start,
                "keys": list(batch_keys),
            })
            batch_start = addr
            batch_end = entry_end
            batch_keys = [(key, 0, count, config)]

    # Finalize last batch
    batches.append({
        "address": batch_start,
        "count": batch_end - batch_start,
        "keys": list(batch_keys),
    })

    return batches


class Bitfield16(BitFlags):
    nbits = 16


class Bitfield32(BitFlags):
    nbits = 32


class SolakonModbusHub:
    """Modbus hub for Solakon ONE device."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        device_id: int,
        scan_interval: int,
    ) -> None:
        """Initialize the Modbus hub."""
        self._hass = hass
        self._host = host
        self._port = port
        self._device_id = device_id
        self.scan_interval = scan_interval
        self._lock = asyncio.Lock()
        # Create client exactly like the working script
        self._client = AsyncModbusTcpClient(
            host=self._host,
            port=self._port,
            timeout=5,  # Same timeout as working script
        )
        # Pre-compute batched register groups for efficient reading
        self._dynamic_batches = compute_register_batches(REGISTERS, static=False)
        self._static_batches = compute_register_batches(REGISTERS, static=True)
        self._static_data: dict[str, Any] = {}

        _LOGGER.debug(
            "Computed %d dynamic batches and %d static batches from %d registers",
            len(self._dynamic_batches),
            len(self._static_batches),
            len(REGISTERS),
        )

    @property
    def connected(self) -> bool:
        """Check if client is connected."""
        return self._client is not None and self._client.connected

    async def async_setup(self) -> None:
        """Set up the Modbus connection."""
        try:
            _LOGGER.info(
                f"Attempting to connect to Modbus TCP at {self._host}:{self._port}"
            )

            # Connect to the device
            await self._client.connect()

            if self._client.connected:
                _LOGGER.info(f"Successfully connected to {self._host}:{self._port}")

                # Test the connection with a simple read
                # Using device_id parameter like the working script
                try:
                    test_result = await self._client.read_holding_registers(
                        address=30000,
                        count=1,
                        device_id=self._device_id,  # Using device_id like your working script
                    )

                    if test_result.isError():
                        _LOGGER.warning(f"Test read returned error: {test_result}")
                    else:
                        _LOGGER.info(
                            f"Test read successful, device_id={self._device_id}"
                        )
                except Exception as e:
                    _LOGGER.warning(f"Test read exception: {e}")

                # Read static registers once after successful connection
                await self._async_read_static_registers()
            else:
                _LOGGER.error(f"Failed to connect to {self._host}:{self._port}")
                raise CannotConnect(f"Failed to connect to {self._host}:{self._port}")

        except Exception as err:
            _LOGGER.error(f"Connection setup error: {err}")
            raise

    async def async_close(self) -> None:
        """Close the Modbus connection."""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass

    async def async_test_connection(self) -> bool:
        """Test the Modbus connection."""
        try:
            if not self._client:
                await self.async_setup()

            if not self.connected:
                _LOGGER.error("Client not connected for test")
                return False

            # Test with device_id parameter (like your working script)
            _LOGGER.debug(
                f"Testing connection to {self._host}:{self._port} with device_id={self._device_id}"
            )

            result = await self._client.read_holding_registers(
                address=30000,  # Model name register
                count=1,
                device_id=self._device_id,  # Using device_id
            )

            if not result.isError():
                _LOGGER.info("Connection test successful")
                return True

            _LOGGER.error(f"Connection test failed: {result}")
            return False

        except Exception as err:
            _LOGGER.error(f"Connection test error: {err}")
            return False

    async def async_get_device_info(self) -> dict[str, Any]:
        """Get device information."""
        try:
            if not self.connected:
                await self.async_setup()

            if not self._client or not self.connected:
                return {
                    "manufacturer": DEFAULT_MANUFACTURER,
                    "name": DEFAULT_NAME,
                }

            model_name = None
            serial_number = None

            try:
                model_result = await self._client.read_holding_registers(
                    address=30000, count=16, device_id=self._device_id
                )

                serial_result = await self._client.read_holding_registers(
                    address=30016, count=16, device_id=self._device_id
                )

                if not model_result.isError():
                    model_name = convert_string(model_result.registers)
                if not serial_result.isError():
                    serial_number = convert_string(serial_result.registers)

            except Exception as e:
                _LOGGER.debug(f"Device info read error: {e}")

            return {
                "manufacturer": DEFAULT_MANUFACTURER,
                "model": model_name,
                "name": model_name or DEFAULT_NAME,
                "serial_number": serial_number,
            }

        except Exception as err:
            _LOGGER.error(f"Failed to get device info: {err}")
            return {
                "manufacturer": DEFAULT_MANUFACTURER,
                "name": DEFAULT_NAME,
            }

    async def _async_read_batches(
        self, batches: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Read a list of register batches and return processed values."""
        data: dict[str, Any] = {}

        for batch in batches:
            batch_start = time.monotonic()
            batch_addr = batch["address"]
            batch_count = batch["count"]
            batch_keys = batch["keys"]
            key_names = [k[0] for k in batch_keys]

            try:
                result = await self._client.read_holding_registers(
                    address=batch_addr,
                    count=batch_count,
                    device_id=self._device_id,
                )

                if result.isError():
                    _LOGGER.error(
                        "Error reading batch at address %d (count=%d, keys=%s): %s",
                        batch_addr, batch_count, key_names, result,
                    )
                    continue

                # Extract each key's registers from the batch result
                for key, offset, count, config in batch_keys:
                    key_regs = result.registers[offset : offset + count]
                    value = self._process_register_value(key_regs, config)
                    if value is not None:
                        data[key] = value

            except Exception as err:
                _LOGGER.error(
                    "Failed to read batch at address %d (count=%d, keys=%s): %s",
                    batch_addr, batch_count, key_names, err,
                )
            finally:
                batch_elapsed = time.monotonic() - batch_start
                _LOGGER.debug(
                    "Batch at address %d (%d regs, %d keys) took %.3fs",
                    batch_addr, batch_count, len(batch_keys), batch_elapsed,
                )

        return data

    async def _async_read_static_registers(self) -> None:
        """Read static registers (device info, versions) once."""
        if not self._static_batches:
            return

        _LOGGER.debug("Reading %d static register batches", len(self._static_batches))
        start = time.monotonic()

        async with self._lock:
            self._static_data = await self._async_read_batches(self._static_batches)

        elapsed = time.monotonic() - start
        _LOGGER.debug(
            "Static registers read complete: %d values in %.3fs",
            len(self._static_data), elapsed,
        )

    async def async_read_registers(self) -> dict[str, Any]:
        """Read all configured registers using batched reads."""
        data: dict[str, Any] = {}

        if not self._client or not self.connected:
            try:
                await self.async_setup()
            except Exception:
                return data

        if not self.connected:
            _LOGGER.error("Client not connected for register read")
            return data

        async with self._lock:
            lock_start = time.monotonic()
            data = await self._async_read_batches(self._dynamic_batches)
            lock_elapsed = time.monotonic() - lock_start
            _LOGGER.debug(
                "Lock held for %.3fs total. Register read: %d batches and %d values",
                lock_elapsed, len(self._dynamic_batches), len(data),
            )

        # Merge in static data (read once at setup)
        if self._static_data:
            data.update(self._static_data)

        return data

    async def async_read_all_data(self) -> dict[str, Any]:
        """Read all data from the device."""
        return await self.async_read_registers()

    def _process_register_value(
        self, registers: list[int], config: dict[str, Any]
    ) -> Any:
        """Process register values based on their configuration."""
        if not registers:
            return None

        data_type = str(config.get("type", "uint16"))
        scale = float(config.get("scale", 1))
        value: Any = None

        try:
            if data_type in ("uint16", "u16"):
                value = registers[0]
            elif data_type in ("int16", "i16"):
                value = registers[0]
                if value > 0x7FFF:  # Using same conversion as working script
                    value = value - 0x10000
            elif data_type in ("uint32", "u32"):
                if len(registers) < 2:
                    return None
                value = (registers[0] << 16) | registers[1]
            elif data_type in ("int32", "i32"):
                if len(registers) < 2:
                    return None
                value = (registers[0] << 16) | registers[1]
                if value > 0x7FFFFFFF:  # Using same conversion as working script
                    value = value - 0x100000000
            elif data_type in ("bitfield16"):
                value = convert_bitfield16(registers, config.get("bit", 0))
            elif data_type in ("bitfield32"):
                value = convert_bitfield32(registers, config.get("bit", 0))
            elif data_type == "string":
                return convert_string(registers)
            else:
                value = registers[0]

            # Apply scaling if defined
            if scale != 1 and value is not None:
                value = float(value) / scale
            return value

        except Exception as err:
            _LOGGER.debug(f"Failed to process register value: {err}")
            return None

    async def async_write_register(self, address: int, value: int) -> bool:
        """Write a single register."""
        if not self.connected:
            return False

        async with self._lock:
            try:
                # Using device_id parameter
                result = await self._client.write_register(
                    address=address, value=value, device_id=self._device_id
                )

                return not result.isError()

            except Exception as err:
                _LOGGER.error(f"Failed to write register at {address}: {err}")
                return False

    async def async_write_registers(self, address: int, values: list[int]) -> bool:
        """Write multiple registers."""
        if not self.connected:
            return False

        async with self._lock:
            try:
                # Using device_id parameter
                result = await self._client.write_registers(
                    address=address, values=values, device_id=self._device_id
                )

                return not result.isError()

            except Exception as err:
                _LOGGER.error(f"Failed to write registers at {address}: {err}")
                return False


def get_modbus_hub(hass: HomeAssistant, data: ConfigEntry) -> SolakonModbusHub:
    """Creates the hub to interact with the modbus."""
    return SolakonModbusHub(
        hass,
        data[CONF_HOST],
        data[CONF_PORT],
        data.get(CONF_DEVICE_ID, DEFAULT_DEVICE_ID),
        data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )


def convert_bitfield16(registers: list[int], bit: int) -> bool | None:
    """Convert bitfield16 registers to boolean."""
    if bit > 15:
        return None
    bitfield = Bitfield16(registers[0])
    return bool(bitfield[f"bit_{bit}"])


def convert_bitfield32(registers: list[int], bit: int) -> bool | None:
    """Convert bitfield32 registers to boolean."""
    if len(registers) < 2 or bit > 31:
        return None
    bitfield = Bitfield32((registers[0] << 16) | registers[1])
    return bool(bitfield[f"bit_{bit}"])


def convert_string(registers: list[int]) -> str | None:
    """Convert registers to string."""
    chars = []
    for val in registers:
        chars.append(chr((val >> 8) & 0xFF))
        chars.append(chr(val & 0xFF))
    text = "".join(chars).rstrip("\x00").strip()
    return text if text else None
