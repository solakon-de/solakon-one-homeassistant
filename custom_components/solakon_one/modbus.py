"""Modbus communication for Solakon ONE."""

from __future__ import annotations

import asyncio
import logging
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

    async def async_read_registers(self) -> dict[str, Any]:
        """Read all configured registers."""
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
            for key, config in REGISTERS.items():
                try:
                    # Read register with device_id parameter (like working script)
                    result = await self._client.read_holding_registers(
                        address=config["address"],
                        count=config.get("count", 1),
                        device_id=self._device_id,
                    )

                    if result.isError():
                        _LOGGER.debug(
                            f"Error reading register {key} at address {config['address']}: {result}"
                        )
                        continue

                    # Process the register value
                    value = self._process_register_value(result.registers, config)

                    if value is not None:
                        data[key] = value

                except Exception as err:
                    _LOGGER.debug(
                        f"Failed to read register {key} at address {config.get('address', 'unknown')}: {err}"
                    )

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
