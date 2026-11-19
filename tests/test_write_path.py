"""Tests for writing values: register encoding and write errors reaching the caller."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.solakon_one.const import REGISTERS
from custom_components.solakon_one.modbus import SolakonModbusHub
from custom_components.solakon_one.number import (
    FORCE_DURATION_NUMBER_ENTITY_DESCRIPTION,
    NUMBER_ENTITY_DESCRIPTIONS,
    ForceDurationNumber,
    SolakonNumber,
)
from custom_components.solakon_one.select import (
    SELECT_ENTITY_DESCRIPTIONS,
    SolakonSelect,
)


class _FakeClient:
    """Modbus client that stores written registers and answers reads from them."""

    def __init__(self, error: bool = False) -> None:
        self.connected = True
        self.error = error
        self.registers: dict[int, int] = {}

    def _result(self):
        return SimpleNamespace(isError=lambda: self.error)

    async def write_register(self, address, value, device_id):
        self.registers[address] = value
        return self._result()

    async def write_registers(self, address, values, device_id):
        for offset, value in enumerate(values):
            self.registers[address + offset] = value
        return self._result()

    async def read_holding_registers(self, address, count, device_id):
        return SimpleNamespace(
            isError=lambda: False,
            registers=[self.registers.get(address + i, 0) for i in range(count)],
        )


def make_hub(client: _FakeClient | None = None) -> SolakonModbusHub:
    hub = SolakonModbusHub(None, "127.0.0.1", 502, 1, 30)
    hub._client = client or _FakeClient()
    return hub


async def read_back(hub: SolakonModbusHub, key: str):
    config = REGISTERS[key]
    result = await hub._client.read_holding_registers(
        config["address"], config.get("count", 1), 1
    )
    return hub._process_register_value(result.registers, config)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("minimum_soc", 15),
        ("battery_max_charge_current", 12.5),
        ("remote_active_power", -500),
        ("remote_active_power", 800),
        ("remote_timeout_set", 3600),
        ("eps_output", 2),
    ],
)
async def test_written_value_reads_back_unchanged(key: str, value: float) -> None:
    hub = make_hub()

    await hub.async_write_value(key, value)

    assert await read_back(hub, key) == value


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("minimum_soc", -1),
        ("minimum_soc", 0x10000),
        ("remote_active_power", 0x80000000),
    ],
)
async def test_value_outside_the_register_is_rejected(key: str, value: float) -> None:
    hub = make_hub()

    with pytest.raises(ServiceValidationError) as err:
        await hub.async_write_value(key, value)

    assert err.value.translation_key == "value_out_of_range"
    assert hub._client.registers == {}


async def test_error_response_raises() -> None:
    hub = make_hub(_FakeClient(error=True))

    with pytest.raises(HomeAssistantError) as err:
        await hub.async_write_value("minimum_soc", 20)

    assert err.value.translation_key == "write_failed"


async def test_write_without_connection_raises() -> None:
    client = _FakeClient()
    client.connected = False
    hub = make_hub(client)

    with pytest.raises(HomeAssistantError) as err:
        await hub.async_write_value("minimum_soc", 20)

    assert err.value.translation_key == "not_connected"
    assert client.registers == {}


@pytest.fixture
async def entry() -> MagicMock:
    """Config entry whose hub writes to a fake client that rejects every write."""
    entry = MagicMock()
    entry.entry_id = "entry"
    entry.runtime_data.hub = make_hub(_FakeClient(error=True))
    coordinator = entry.runtime_data.coordinator
    coordinator.data = {}
    coordinator.last_update_success = True
    coordinator.async_request_refresh = AsyncMock()
    return entry


@pytest.fixture(autouse=True)
def no_state_write():
    with patch("homeassistant.helpers.entity.Entity.async_write_ha_state"):
        yield


def _number(key: str):
    return next(d for d in NUMBER_ENTITY_DESCRIPTIONS if d.key == key)


async def test_number_write_failure_reaches_the_caller(entry) -> None:
    number = SolakonNumber(entry, {}, _number("minimum_soc"))

    with pytest.raises(HomeAssistantError):
        await number.async_set_native_value(20)

    assert number.native_value is None
    entry.runtime_data.coordinator.async_request_refresh.assert_not_awaited()


async def test_force_duration_write_failure_reaches_the_caller(entry) -> None:
    number = ForceDurationNumber(entry, {}, FORCE_DURATION_NUMBER_ENTITY_DESCRIPTION)

    with pytest.raises(HomeAssistantError):
        await number.async_set_native_value(5)

    assert number.native_value is None


async def test_select_write_failure_reaches_the_caller(entry) -> None:
    select = SolakonSelect(entry, {}, SELECT_ENTITY_DESCRIPTIONS[0])

    with pytest.raises(HomeAssistantError):
        await select.async_select_option("2")

    assert select.current_option is None


@pytest.mark.parametrize("language", ["en", "de"])
def test_write_errors_are_translated(language: str) -> None:
    path = (
        Path(__file__).parents[1]
        / "custom_components/solakon_one/translations"
        / f"{language}.json"
    )
    exceptions = json.loads(path.read_text(encoding="utf-8"))["exceptions"]

    for key in ("write_failed", "not_connected", "value_out_of_range"):
        assert exceptions[key]["message"]
