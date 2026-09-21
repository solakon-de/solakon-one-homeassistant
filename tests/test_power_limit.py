"""Tests for the discharge power limit."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.solakon_one.const import REGISTERS
from custom_components.solakon_one.power_limit import (
    MAX_CHARGE_POWER,
    MAX_DISCHARGE_POWER,
    async_cap_remote_power,
    i32_to_words,
    is_discharge_mode,
    max_force_power,
    validate_power,
)
from custom_components.solakon_one.remote_control import RemoteControlMode

DISCHARGE_MODES = [
    RemoteControlMode.INV_DISCHARGE_PV_PRIORITY,
    RemoteControlMode.BATTERY_DISCHARGE,
    RemoteControlMode.GRID_DISCHARGE,
    RemoteControlMode.INV_DISCHARGE_AC_FIRST,
]
OTHER_MODES = [mode for mode in RemoteControlMode if mode not in DISCHARGE_MODES]


def test_limit_is_800_watt() -> None:
    assert MAX_DISCHARGE_POWER == 800


@pytest.mark.parametrize("mode", DISCHARGE_MODES)
def test_discharge_modes_are_detected(mode: RemoteControlMode) -> None:
    assert is_discharge_mode(int(mode))
    assert max_force_power(int(mode)) == MAX_DISCHARGE_POWER


@pytest.mark.parametrize("mode", OTHER_MODES)
def test_other_modes_are_not_discharge(mode: RemoteControlMode) -> None:
    assert not is_discharge_mode(int(mode))
    assert max_force_power(int(mode)) == MAX_CHARGE_POWER


def test_generation_direction_without_enable_bit_is_not_discharge() -> None:
    assert not is_discharge_mode(0b0100)


@pytest.mark.parametrize("value", [None, "1", object()])
def test_unknown_mode_is_not_discharge(value: object) -> None:
    assert not is_discharge_mode(value)


@pytest.mark.parametrize("mode", list(RemoteControlMode))
def test_grid_export_limit_never_above_800(mode: RemoteControlMode) -> None:
    validate_power("grid_export_power_limit", 800, int(mode))
    with pytest.raises(ServiceValidationError):
        validate_power("grid_export_power_limit", 810, int(mode))


def test_force_power_depends_on_mode() -> None:
    validate_power("force_power", 1200, int(RemoteControlMode.INV_CHARGE_PV_PRIORITY))
    validate_power("force_power", 1200, int(RemoteControlMode.DISABLED))
    validate_power("force_power", 800, int(RemoteControlMode.INV_DISCHARGE_PV_PRIORITY))
    with pytest.raises(ServiceValidationError):
        validate_power(
            "force_power", 810, int(RemoteControlMode.INV_DISCHARGE_PV_PRIORITY)
        )
    with pytest.raises(ServiceValidationError):
        validate_power(
            "force_power", 1210, int(RemoteControlMode.INV_CHARGE_PV_PRIORITY)
        )


@pytest.mark.parametrize("mode", DISCHARGE_MODES)
@pytest.mark.parametrize("value", [801, -801, 100000, -100000])
def test_remote_active_power_is_limited_while_discharging(
    mode: RemoteControlMode, value: int
) -> None:
    with pytest.raises(ServiceValidationError):
        validate_power("remote_active_power", value, int(mode))


def test_remote_active_power_charging_is_not_limited() -> None:
    validate_power(
        "remote_active_power", -1200, int(RemoteControlMode.INV_CHARGE_PV_PRIORITY)
    )


def test_unrelated_register_is_not_limited() -> None:
    validate_power("remote_timeout_set", 3600, int(RemoteControlMode.BATTERY_DISCHARGE))


@pytest.mark.parametrize(
    ("value", "words"),
    [(800, [0, 800]), (0x12345, [0x1, 0x2345]), (-800, [0xFFFF, 0xFCE0])],
)
def test_i32_to_words(value: int, words: list[int]) -> None:
    assert i32_to_words(value) == words


async def test_cap_lowers_setpoints_above_limit() -> None:
    hub = AsyncMock()
    hub.async_write_registers.return_value = True

    await async_cap_remote_power(
        hub, {"remote_active_power": 1200, "remote_reactive_power": -1200}
    )

    assert hub.async_write_registers.await_args_list == [
        ((REGISTERS["remote_active_power"]["address"], [0, 800]),),
        ((REGISTERS["remote_reactive_power"]["address"], [0xFFFF, 0xFCE0]),),
    ]


async def test_cap_leaves_setpoints_within_limit() -> None:
    hub = AsyncMock()

    await async_cap_remote_power(
        hub, {"remote_active_power": 800, "remote_reactive_power": 0}
    )

    hub.async_write_registers.assert_not_awaited()


@pytest.mark.parametrize(
    "data", [None, {}, {"remote_active_power": None, "remote_reactive_power": 0}]
)
async def test_cap_fails_when_setpoint_is_unknown(data: dict | None) -> None:
    hub = AsyncMock()

    with pytest.raises(HomeAssistantError) as err:
        await async_cap_remote_power(hub, data)

    assert err.value.translation_key == "discharge_setpoint_unknown"


async def test_cap_fails_when_write_fails() -> None:
    hub = AsyncMock()
    hub.async_write_registers.return_value = False

    with pytest.raises(HomeAssistantError) as err:
        await async_cap_remote_power(
            hub, {"remote_active_power": 1200, "remote_reactive_power": 0}
        )

    assert err.value.translation_key == "discharge_setpoint_write_failed"
