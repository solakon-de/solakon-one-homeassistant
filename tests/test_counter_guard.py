"""Tests for lifetime energy counters that must never decrease."""

from types import SimpleNamespace
from typing import Any, cast

import pytest

from custom_components.solakon_one.sensor import (
    SENSOR_ENTITY_DESCRIPTIONS,
    SolakonSensor,
)


def _description(key: str):
    return next(d for d in SENSOR_ENTITY_DESCRIPTIONS if d.key == key)


def _sensor(key: str, data: dict) -> SolakonSensor:
    sensor = SolakonSensor.__new__(SolakonSensor)
    sensor.entity_description = _description(key)
    sensor.coordinator = SimpleNamespace(data=data, last_update_success=True)
    sensor._attr_native_value = None
    sensor._counter_last = None
    cast(Any, sensor).async_write_ha_state = lambda: None
    return sensor


def _feed(sensor: SolakonSensor, key: str, values: list) -> list:
    states = []
    for value in values:
        sensor.coordinator.data = {key: value}
        sensor._handle_coordinator_update()
        states.append(sensor._attr_native_value)
    return states


@pytest.mark.parametrize(
    "key",
    [
        "pv_total_energy",
        "cumulative_generation",
        "battery_total_charge_energy",
        "battery_total_discharge_energy",
        "grid_total_export_energy",
        "grid_total_import_energy",
    ],
)
def test_lifetime_counters_ignore_lower_and_negative_readings(key: str) -> None:
    sensor = _sensor(key, {})

    assert _feed(sensor, key, [25.54, 25.56, 12.31, 25.57, -3.0, 0, 25.58]) == [
        25.54,
        25.56,
        25.56,
        25.57,
        25.57,
        25.57,
        25.58,
    ]


def test_daily_counters_may_reset() -> None:
    sensor = _sensor("pv_daily_energy", {})

    assert _feed(sensor, "pv_daily_energy", [3.2, 3.4, 0.0, 0.1]) == [
        3.2,
        3.4,
        0.0,
        0.1,
    ]


def test_guard_survives_a_poll_without_the_value() -> None:
    key = "pv_total_energy"
    sensor = _sensor(key, {})

    assert _feed(sensor, key, [10.0]) == [10.0]
    sensor.coordinator.data = {}
    sensor._handle_coordinator_update()
    assert sensor._attr_native_value is None
    assert _feed(sensor, key, [4.2, 10.1]) == [None, 10.1]
