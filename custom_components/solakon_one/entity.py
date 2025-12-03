"""Entities for the Solakon integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity




class SolakonEntity(CoordinatorEntity, Entity):
    """Base class for Solakon ONE entities."""


    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        device_info: dict,
        definition: dict,
        key: str,
    ) -> None:
        """Initialize the solakon ONE entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._device_info = device_info
        self._definition = definition

        # Set unique ID and entity ID
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"

        # Set basic attributes
        self._attr_name = definition["name"]
        self._attr_icon = definition.get("icon")
