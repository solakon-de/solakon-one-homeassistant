"""Entities for the Solakon ONE integration."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_MANUFACTURER, DEFAULT_MODEL, DEFAULT_NAME, DOMAIN
from .types import SolakonConfigEntry


class SolakonEntity(CoordinatorEntity, Entity):
    """Base class for Solakon ONE entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: SolakonConfigEntry,
        device_info: dict,
        key: str,
    ) -> None:
        """Initialize the solakon ONE entity."""
        super().__init__(config_entry.runtime_data.coordinator)
        self._config_entry = config_entry

        # Set unique ID
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"
        self._attr_translation_key = key

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=self._config_entry.data.get("name", DEFAULT_NAME),
            model_id=device_info.get("model") or None,
            sw_version=device_info.get("version"),
            serial_number=device_info.get("serial_number"),
            default_model=DEFAULT_MODEL,
            default_manufacturer=DEFAULT_MANUFACTURER,
        )
