"""Tests for setting up the config entry and the device info."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.solakon_one import async_setup_entry
from custom_components.solakon_one.modbus import SolakonModbusHub
from custom_components.solakon_one.sensor import format_version


def _hub(test_connection: bool = True, setup_error: Exception | None = None):
    hub = MagicMock()
    hub.async_setup = AsyncMock(side_effect=setup_error)
    hub.async_test_connection = AsyncMock(return_value=test_connection)
    hub.async_close = AsyncMock()
    return hub


@pytest.mark.parametrize(
    "hub",
    [_hub(test_connection=False), _hub(setup_error=OSError("refused"))],
)
async def test_failed_setup_closes_the_connection(hub) -> None:
    entry = MagicMock(data={}, options={})
    with (
        patch("custom_components.solakon_one.get_modbus_hub", return_value=hub),
        patch("custom_components.solakon_one.polled_keys", return_value=set()),
        pytest.raises(ConfigEntryNotReady),
    ):
        await async_setup_entry(MagicMock(), entry)

    hub.async_close.assert_awaited_once()


async def test_device_info_comes_from_the_static_registers() -> None:
    hub = SolakonModbusHub(None, "127.0.0.1", 502, 1, 30)
    hub._static_data = {"model_name": "SOLAKON ONE", "serial_number": "SN1"}

    assert hub.device_info == {"model": "SOLAKON ONE", "serial_number": "SN1"}


async def test_device_info_without_static_registers_is_empty() -> None:
    hub = SolakonModbusHub(None, "127.0.0.1", 502, 1, 30)

    assert hub.device_info == {"model": None, "serial_number": None}


@pytest.mark.parametrize(("raw", "text"), [(0x020A, "2.010"), (0x0100, "1.000")])
def test_format_version(raw: int, text: str) -> None:
    assert format_version(raw) == text
