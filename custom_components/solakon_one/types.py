"""Types for the Solakon ONE integration."""
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry

from .coordinator import SolakonDataCoordinator
from .modbus import SolakonModbusHub

@dataclass(frozen=True)
class SolakonData:
    """Solakon ONE data class."""

    hub: SolakonModbusHub
    coordinator: SolakonDataCoordinator


type SolakonConfigEntry = ConfigEntry[SolakonData]
