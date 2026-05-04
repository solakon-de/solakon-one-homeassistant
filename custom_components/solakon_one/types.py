"""Types for the Solakon ONE integration."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry

from .coordinator import SolakonDataCoordinator
from .ir_meter import SolakonIRMeterClient
from .modbus import SolakonModbusHub


@dataclass(frozen=True)
class SolakonData:
    """Solakon ONE data class."""

    hub: SolakonModbusHub
    coordinator: SolakonDataCoordinator
    ir_meter: SolakonIRMeterClient | None = None


type SolakonConfigEntry = ConfigEntry[SolakonData]
