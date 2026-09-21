"""Discharge power limit for Solakon ONE integration.

The device must never be commanded to output more than MAX_DISCHARGE_POWER.
Charging is not affected by this limit.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from typing import Any, Protocol, cast
from weakref import WeakKeyDictionary

from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, REGISTERS
from .remote_control import RemoteControlDirection, decode_remote_control

_LOGGER = logging.getLogger(__name__)

MAX_DISCHARGE_POWER = 800  # W
MAX_CHARGE_POWER = 1200  # W

# Setpoints that are used as the power command while remote control is active
REMOTE_POWER_KEYS = ("remote_active_power", "remote_reactive_power")

_LOCKS: WeakKeyDictionary[DataUpdateCoordinator, asyncio.Lock] = WeakKeyDictionary()


def discharge_lock(coordinator: DataUpdateCoordinator) -> asyncio.Lock:
    """Return the lock that serializes mode and power setpoint writes of a device.

    Checking the limit and writing the register must not interleave with another
    write, otherwise a mode switch and a setpoint change can pass each other.
    """
    return _LOCKS.setdefault(coordinator, asyncio.Lock())


async def async_fresh_data(
    coordinator: DataUpdateCoordinator,
) -> Mapping[str, Any] | None:
    """Read the device now and return the data, None if the read failed.

    coordinator.data can't be used for the limit: async_request_refresh is
    debounced, so after a write it may hold outdated values for a whole scan interval.
    """
    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        return None
    return coordinator.data


class RegisterWriter(Protocol):
    """Part of the modbus hub that is needed to write a setpoint."""

    async def async_write_registers(self, address: int, values: list[int]) -> bool:
        """Write multiple registers."""


def is_discharge_mode(remote_control_value: object) -> bool:
    """Return if the remote control register value commands a discharge.

    An unknown value counts as discharge, so that the limit applies.
    """
    if not isinstance(remote_control_value, (int, float)):
        return True
    enabled, direction, _ = decode_remote_control(int(remote_control_value))
    return enabled and direction == RemoteControlDirection.GENERATION


def max_force_power(remote_control_value: object) -> int:
    """Return the highest force mode power for the remote control register value."""
    if is_discharge_mode(remote_control_value):
        return MAX_DISCHARGE_POWER
    return MAX_CHARGE_POWER


def power_range(key: str, remote_control_value: object) -> tuple[int, int] | None:
    """Return the allowed (min, max) for a power setpoint, None if it is not limited.

    remote_active_power is signed: positive values discharge. While a discharge
    mode is active the magnitude is what counts, so both signs are limited.
    """
    if key == "grid_export_power_limit":
        return (0, MAX_DISCHARGE_POWER)
    if key == "force_power":
        return (0, max_force_power(remote_control_value))
    if key in REMOTE_POWER_KEYS and is_discharge_mode(remote_control_value):
        return (-MAX_DISCHARGE_POWER, MAX_DISCHARGE_POWER)
    return None


def validate_power(key: str, value: float, remote_control_value: object) -> None:
    """Raise if the value would allow more than the discharge limit."""
    limits = power_range(key, remote_control_value)
    if limits is None or limits[0] <= value <= limits[1]:
        return
    raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="discharge_power_limit_exceeded",
        translation_placeholders={
            "value": f"{value:g}",
            "min": str(limits[0]),
            "max": str(limits[1]),
        },
    )


async def async_validate_power(
    coordinator: DataUpdateCoordinator, key: str, value: float
) -> None:
    """Raise if the value would allow more than the discharge limit on the device."""
    limits = power_range(key, None)
    if limits is None or limits[0] <= value <= limits[1]:
        # Allowed in every mode
        return
    data = await async_fresh_data(coordinator)
    validate_power(key, value, data.get("remote_control") if data else None)


def i32_to_words(value: int) -> list[int]:
    """Split a signed 32-bit value into high and low word (big-endian)."""
    raw = value & 0xFFFFFFFF
    return [(raw >> 16) & 0xFFFF, raw & 0xFFFF]


async def async_cap_remote_power(
    hub: RegisterWriter, data: Mapping[str, Any] | None
) -> None:
    """Bring the remote power setpoints below the limit before a discharge starts.

    Has to run before a discharge mode is written to the remote control register,
    because the setpoints may still hold a higher value from charging.
    The data has to come from async_fresh_data.
    """
    for key in REMOTE_POWER_KEYS:
        value = data.get(key) if data else None
        if not isinstance(value, (int, float)):
            # Without the current setpoint a discharge above the limit can't be ruled out
            _LOGGER.warning(
                f"Discharge was not enabled because {key} could not be read from the device"
            )
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="discharge_setpoint_unknown",
                translation_placeholders={"key": key},
            )

        capped = max(-MAX_DISCHARGE_POWER, min(MAX_DISCHARGE_POWER, int(value)))
        if capped == int(value):
            continue

        _LOGGER.info(
            f"Limiting {key} from {value} to {capped} before discharge is enabled"
        )
        address = cast(int, REGISTERS[key]["address"])
        if not await hub.async_write_registers(address, i32_to_words(capped)):
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="discharge_setpoint_write_failed",
                translation_placeholders={
                    "key": key,
                    "max": str(MAX_DISCHARGE_POWER),
                },
            )
