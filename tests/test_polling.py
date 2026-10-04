"""Tests for register batching, the slow read interval and the polled keys."""

from types import SimpleNamespace

from custom_components.solakon_one import modbus, polling
from custom_components.solakon_one.binary_sensor import (
    BINARY_SENSOR_ENTITY_DESCRIPTIONS,
)
from custom_components.solakon_one.const import REGISTERS
from custom_components.solakon_one.modbus import (
    SolakonModbusHub,
    compute_register_batches,
)
from custom_components.solakon_one.sensor import SENSOR_ENTITY_DESCRIPTIONS


def _spans(batches):
    return [(b["address"], b["count"]) for b in batches]


def _default_keys():
    descriptions = (*SENSOR_ENTITY_DESCRIPTIONS, *BINARY_SENSOR_ENTITY_DESCRIPTIONS)
    return polling.CONTROL_KEYS | {
        d.data_key or d.key for d in descriptions if d.entity_registry_enabled_default
    }


def test_default_entities_read_five_fast_and_two_slow_batches() -> None:
    keys = _default_keys()
    fast = compute_register_batches(REGISTERS, slow=False, keys=keys)
    slow = compute_register_batches(REGISTERS, slow=True, keys=keys)

    assert _spans(fast) == [
        (39065, 86),
        (39201, 72),
        (39424, 1),
        (46001, 7),
        (46607, 11),
    ]
    assert _spans(slow) == [(37611, 25), (39601, 26)]


def test_gaps_are_bridged_only_inside_verified_spans() -> None:
    fast = compute_register_batches(REGISTERS, slow=False)

    assert (39053, 100) in _spans(fast)
    assert (39201, 86) in _spans(fast)
    # The device truncates bridged reads in the 49xxx range
    assert (49203, 1) in _spans(fast)
    assert (49240, 1) in _spans(compute_register_batches(REGISTERS, slow=True))
    assert (49079, 1) in _spans(compute_register_batches(REGISTERS, static=True))


def test_versions_are_static() -> None:
    static = compute_register_batches(REGISTERS, static=True)

    assert (36001, 3) in _spans(static)
    assert (37003, 1) in _spans(static)


class _FakeClient:
    connected = True

    def __init__(self) -> None:
        self.reads: list[int] = []

    async def read_holding_registers(self, address, count, device_id):
        self.reads.append(address)
        return SimpleNamespace(isError=lambda: False, registers=[0] * count)


async def test_slow_registers_are_read_once_per_interval(monkeypatch) -> None:
    hub = SolakonModbusHub(None, "127.0.0.1", 502, 1, 1)
    hub._client = _FakeClient()
    hub._static_data = {"model_name": "x"}
    now = [1000.0]
    monkeypatch.setattr(modbus.time, "monotonic", lambda: now[0])

    first = await hub.async_read_registers()
    assert 39601 in hub._client.reads
    assert "pv_total_energy" in first

    hub._client.reads.clear()
    now[0] += modbus.SLOW_INTERVAL - 1
    second = await hub.async_read_registers()
    assert 39601 not in hub._client.reads
    assert second["pv_total_energy"] == first["pv_total_energy"]

    hub._client.reads.clear()
    now[0] += 1
    await hub.async_read_registers()
    assert 39601 in hub._client.reads


def test_polled_keys_follow_entity_registry(monkeypatch) -> None:
    entry = SimpleNamespace(entry_id="abc")
    registry_entries = [
        # enabled by default, disabled by the user
        SimpleNamespace(unique_id="abc_battery_soc", disabled_by="user"),
        # disabled by default, enabled by the user
        SimpleNamespace(unique_id="abc_network_status", disabled_by=None),
    ]
    monkeypatch.setattr(polling.er, "async_get", lambda hass: None)
    monkeypatch.setattr(
        polling.er,
        "async_entries_for_config_entry",
        lambda registry, entry_id: registry_entries,
    )

    keys = polling.polled_keys(None, entry)

    assert "battery_soc" not in keys
    assert "network_status" in keys
    # disabled by default and not in the registry
    assert "grid_standard_code" not in keys
    # enabled by default and not in the registry
    assert "battery_power" in keys
    # control registers are always read
    assert polling.CONTROL_KEYS <= keys
