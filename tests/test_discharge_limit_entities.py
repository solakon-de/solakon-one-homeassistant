"""Tests for the discharge power limit on the number and select entities."""

import asyncio
import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.solakon_one.const import REGISTERS
from custom_components.solakon_one.number import (
    FORCE_POWER_NUMBER_ENTITY_DESCRIPTION,
    NUMBER_ENTITY_DESCRIPTIONS,
    ForcePowerNumber,
    SolakonNumber,
)
from custom_components.solakon_one.select import (
    FORCE_MODE_SELECT_ENTITY_DESCRIPTION,
    REMOTE_CONTROLL_MODE_SELECT_ENTITY_DESCRIPTION,
    ForceModeSelect,
    RemoteControlModeSelect,
)

ACTIVE = REGISTERS["remote_active_power"]["address"]
REACTIVE = REGISTERS["remote_reactive_power"]["address"]
REMOTE_CONTROL = REGISTERS["remote_control"]["address"]

FORCE_DISCHARGE = 1
FORCE_CHARGE = 3


@pytest.fixture(autouse=True)
def no_state_write():
    """Entities are not added to a hass instance, so there is no state machine."""
    with patch("homeassistant.helpers.entity.Entity.async_write_ha_state"):
        yield


def make_entry(data: dict[str, Any], device: dict[str, Any] | None = None) -> MagicMock:
    """Create a config entry with a coordinator cache and the values on the device.

    Like the real coordinator, the cache only changes on async_refresh:
    async_request_refresh is debounced and may not read anything after a write.
    """
    entry = MagicMock()
    entry.entry_id = "entry"
    coordinator = entry.runtime_data.coordinator
    coordinator.data = data
    coordinator.last_update_success = True
    coordinator.async_request_refresh = AsyncMock()
    registers = dict(data if device is None else device)

    async def refresh() -> None:
        coordinator.data = dict(registers)

    coordinator.async_refresh = AsyncMock(side_effect=refresh)
    entry.runtime_data.hub.async_write_register = AsyncMock(return_value=True)
    entry.runtime_data.hub.async_write_registers = AsyncMock(return_value=True)
    return entry


def description(key: str):
    return next(d for d in NUMBER_ENTITY_DESCRIPTIONS if d.key == key)


def test_static_maximums() -> None:
    assert description("grid_export_power_limit").native_max_value == 800
    assert description("remote_active_power").native_max_value == 800


async def test_grid_export_power_limit_rejects_more_than_800() -> None:
    entry = make_entry({"remote_control": 0})
    number = SolakonNumber(entry, {}, description("grid_export_power_limit"))

    with pytest.raises(ServiceValidationError):
        await number.async_set_native_value(1200)
    entry.runtime_data.hub.async_write_registers.assert_not_awaited()

    await number.async_set_native_value(800)
    entry.runtime_data.hub.async_write_registers.assert_awaited_once_with(
        REGISTERS["grid_export_power_limit"]["address"], [0, 800]
    )


async def test_remote_active_power_magnitude_limited_while_discharging() -> None:
    entry = make_entry({"remote_control": FORCE_DISCHARGE})
    number = SolakonNumber(entry, {}, description("remote_active_power"))

    with pytest.raises(ServiceValidationError):
        await number.async_set_native_value(-1200)
    entry.runtime_data.hub.async_write_registers.assert_not_awaited()


async def test_remote_active_power_charging_still_allowed() -> None:
    entry = make_entry({"remote_control": FORCE_CHARGE})
    number = SolakonNumber(entry, {}, description("remote_active_power"))

    await number.async_set_native_value(-1200)

    entry.runtime_data.hub.async_write_registers.assert_awaited_once()


@pytest.mark.parametrize(
    ("remote_control", "maximum"),
    [(FORCE_DISCHARGE, 800), (FORCE_CHARGE, 1200), (0, 1200), (None, 800)],
)
def test_force_power_maximum_follows_mode(
    remote_control: int | None, maximum: int
) -> None:
    entry = make_entry({"remote_control": remote_control})
    number = ForcePowerNumber(entry, {}, FORCE_POWER_NUMBER_ENTITY_DESCRIPTION)

    assert number.native_max_value == maximum
    assert number.max_value == maximum


async def test_force_power_rejects_more_than_800_while_discharging() -> None:
    entry = make_entry({"remote_control": FORCE_DISCHARGE})
    number = ForcePowerNumber(entry, {}, FORCE_POWER_NUMBER_ENTITY_DESCRIPTION)

    with pytest.raises(ServiceValidationError):
        await number.async_set_native_value(1200)
    entry.runtime_data.hub.async_write_registers.assert_not_awaited()

    await number.async_set_native_value(800)
    assert [
        c.args for c in entry.runtime_data.hub.async_write_registers.await_args_list
    ] == [
        (ACTIVE, [0, 800]),
        (REACTIVE, [0, 800]),
    ]


async def test_force_power_allows_1200_while_charging() -> None:
    entry = make_entry({"remote_control": FORCE_CHARGE})
    number = ForcePowerNumber(entry, {}, FORCE_POWER_NUMBER_ENTITY_DESCRIPTION)

    await number.async_set_native_value(1200)

    assert entry.runtime_data.hub.async_write_registers.await_count == 2


async def test_force_power_is_checked_against_the_mode_on_the_device() -> None:
    """The cache still says charge, the refresh after the mode switch was debounced."""
    entry = make_entry(
        {"remote_control": FORCE_CHARGE}, device={"remote_control": FORCE_DISCHARGE}
    )
    number = ForcePowerNumber(entry, {}, FORCE_POWER_NUMBER_ENTITY_DESCRIPTION)

    with pytest.raises(ServiceValidationError):
        await number.async_set_native_value(1200)

    entry.runtime_data.hub.async_write_registers.assert_not_awaited()


async def test_force_power_above_800_is_rejected_when_device_cannot_be_read() -> None:
    entry = make_entry({"remote_control": FORCE_CHARGE})
    entry.runtime_data.coordinator.last_update_success = False
    number = ForcePowerNumber(entry, {}, FORCE_POWER_NUMBER_ENTITY_DESCRIPTION)

    with pytest.raises(ServiceValidationError):
        await number.async_set_native_value(1200)
    entry.runtime_data.hub.async_write_registers.assert_not_awaited()

    await number.async_set_native_value(800)
    assert entry.runtime_data.hub.async_write_registers.await_count == 2


async def test_remote_active_power_is_checked_against_the_mode_on_the_device() -> None:
    entry = make_entry(
        {"remote_control": FORCE_CHARGE}, device={"remote_control": FORCE_DISCHARGE}
    )
    number = SolakonNumber(entry, {}, description("remote_active_power"))

    with pytest.raises(ServiceValidationError):
        await number.async_set_native_value(-1200)

    entry.runtime_data.hub.async_write_registers.assert_not_awaited()


SELECTS = [
    (ForceModeSelect, FORCE_MODE_SELECT_ENTITY_DESCRIPTION, "1"),
    (RemoteControlModeSelect, REMOTE_CONTROLL_MODE_SELECT_ENTITY_DESCRIPTION, "1"),
    (RemoteControlModeSelect, REMOTE_CONTROLL_MODE_SELECT_ENTITY_DESCRIPTION, "5"),
    (RemoteControlModeSelect, REMOTE_CONTROLL_MODE_SELECT_ENTITY_DESCRIPTION, "9"),
    (RemoteControlModeSelect, REMOTE_CONTROLL_MODE_SELECT_ENTITY_DESCRIPTION, "13"),
]


@pytest.mark.parametrize(("cls", "desc", "option"), SELECTS)
async def test_switching_to_discharge_caps_the_setpoints_first(
    cls, desc, option: str
) -> None:
    entry = make_entry(
        {
            "remote_control": FORCE_CHARGE,
            "remote_active_power": 1200,
            "remote_reactive_power": 1200,
        }
    )
    hub = entry.runtime_data.hub
    calls: list[tuple] = []

    def record(*args: Any) -> bool:
        calls.append(args)
        return True

    hub.async_write_registers.side_effect = record
    hub.async_write_register.side_effect = record

    await cls(entry, {}, desc).async_select_option(option)

    assert calls == [
        (ACTIVE, [0, 800]),
        (REACTIVE, [0, 800]),
        (REMOTE_CONTROL, int(option)),
    ]


@pytest.mark.parametrize(("cls", "desc", "option"), SELECTS)
async def test_discharge_is_not_enabled_when_the_cap_fails(
    cls, desc, option: str
) -> None:
    entry = make_entry(
        {
            "remote_control": FORCE_CHARGE,
            "remote_active_power": 1200,
            "remote_reactive_power": 1200,
        }
    )
    entry.runtime_data.hub.async_write_registers.return_value = False

    with pytest.raises(HomeAssistantError):
        await cls(entry, {}, desc).async_select_option(option)

    entry.runtime_data.hub.async_write_register.assert_not_awaited()


@pytest.mark.parametrize(("cls", "desc", "option"), SELECTS)
async def test_switching_to_discharge_caps_setpoints_the_cache_does_not_know(
    cls, desc, option: str
) -> None:
    """The cache still holds 300 W, the refresh after writing 1200 W was debounced."""
    entry = make_entry(
        {
            "remote_control": FORCE_CHARGE,
            "remote_active_power": 300,
            "remote_reactive_power": 300,
        },
        device={
            "remote_control": FORCE_CHARGE,
            "remote_active_power": 1200,
            "remote_reactive_power": 1200,
        },
    )

    await cls(entry, {}, desc).async_select_option(option)

    hub = entry.runtime_data.hub
    assert [c.args for c in hub.async_write_registers.await_args_list] == [
        (ACTIVE, [0, 800]),
        (REACTIVE, [0, 800]),
    ]
    hub.async_write_register.assert_awaited_once_with(REMOTE_CONTROL, int(option))


@pytest.mark.parametrize(("cls", "desc", "option"), SELECTS)
async def test_discharge_is_not_enabled_when_the_device_cannot_be_read(
    cls, desc, option: str
) -> None:
    entry = make_entry(
        {
            "remote_control": FORCE_CHARGE,
            "remote_active_power": 300,
            "remote_reactive_power": 300,
        }
    )
    entry.runtime_data.coordinator.last_update_success = False

    with pytest.raises(HomeAssistantError):
        await cls(entry, {}, desc).async_select_option(option)

    entry.runtime_data.hub.async_write_register.assert_not_awaited()


async def test_mode_switch_waits_for_a_running_setpoint_write() -> None:
    """A setpoint validated for charging has to land before the cap reads the device."""
    device = {
        "remote_control": FORCE_CHARGE,
        "remote_active_power": 300,
        "remote_reactive_power": 300,
    }
    entry = make_entry(dict(device), device=device)
    coordinator = entry.runtime_data.coordinator
    hub = entry.runtime_data.hub
    by_address = {ACTIVE: "remote_active_power", REACTIVE: "remote_reactive_power"}

    async def refresh() -> None:
        await asyncio.sleep(0)
        coordinator.data = dict(device)

    async def write_registers(address: int, values: list[int]) -> bool:
        await asyncio.sleep(0)
        device[by_address[address]] = values[1]
        return True

    async def write_register(address: int, value: int) -> bool:
        device["remote_control"] = value
        return True

    coordinator.async_refresh.side_effect = refresh
    hub.async_write_registers.side_effect = write_registers
    hub.async_write_register.side_effect = write_register

    number = ForcePowerNumber(entry, {}, FORCE_POWER_NUMBER_ENTITY_DESCRIPTION)
    select = ForceModeSelect(entry, {}, FORCE_MODE_SELECT_ENTITY_DESCRIPTION)
    await asyncio.gather(
        number.async_set_native_value(1200), select.async_select_option("1")
    )

    assert device == {
        "remote_control": FORCE_DISCHARGE,
        "remote_active_power": 800,
        "remote_reactive_power": 800,
    }


async def test_switching_to_charge_does_not_touch_the_setpoints() -> None:
    entry = make_entry(
        {
            "remote_control": 0,
            "remote_active_power": 1200,
            "remote_reactive_power": 1200,
        }
    )

    await ForceModeSelect(
        entry, {}, FORCE_MODE_SELECT_ENTITY_DESCRIPTION
    ).async_select_option("3")

    entry.runtime_data.hub.async_write_registers.assert_not_awaited()
    entry.runtime_data.hub.async_write_register.assert_awaited_once_with(
        REMOTE_CONTROL, FORCE_CHARGE
    )


@pytest.mark.parametrize("language", ["en", "de"])
def test_exception_messages_are_translated(language: str) -> None:
    path = (
        Path(__file__).parents[1]
        / "custom_components/solakon_one/translations"
        / f"{language}.json"
    )
    exceptions = json.loads(path.read_text(encoding="utf-8"))["exceptions"]

    assert set(exceptions) == {
        "discharge_power_limit_exceeded",
        "discharge_setpoint_unknown",
        "discharge_setpoint_write_failed",
    }
