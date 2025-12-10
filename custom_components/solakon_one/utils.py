"""The Solakon ONE integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant

from .const import CONF_DEVICE_ID, DEFAULT_DEVICE_ID, DEFAULT_SCAN_INTERVAL
from .modbus import SolakonModbusHub


_LOGGER = logging.getLogger(__name__)


def create_hub(hass : HomeAssistant, data: ConfigEntry) -> SolakonModbusHub:
    return SolakonModbusHub(
        hass,
        data[CONF_HOST],
        data[CONF_PORT],
        data.get(CONF_DEVICE_ID, DEFAULT_DEVICE_ID),
        data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
