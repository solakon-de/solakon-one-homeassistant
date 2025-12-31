"""Types for the Solakon ONE integration."""
from dataclasses import dataclass
from typing import Union

from homeassistant.config_entries import ConfigEntry

from .coordinator import IRMeterDataCoordinator, SolakonDataCoordinator
from .ir_meter import IRMeterHub
from .modbus import SolakonModbusHub


@dataclass(frozen=True)
class SolakonData:
    """Solakon ONE data class."""

    hub: SolakonModbusHub
    coordinator: SolakonDataCoordinator


@dataclass(frozen=True)
class IRMeterData:
    """IR Meter data class."""

    hub: IRMeterHub
    coordinator: IRMeterDataCoordinator


type SolakonConfigEntry = ConfigEntry[SolakonData]
type IRMeterConfigEntry = ConfigEntry[IRMeterData]
type SolakonOrIRMeterConfigEntry = ConfigEntry[Union[SolakonData, IRMeterData]]
