"""Binary sensor platform for Solakon ONE integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import SolakonEntity
from .types import SolakonConfigEntry

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SolakonBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Solakon binary sensor entity description."""

    data_key: str | None = None
    value_fn: Callable[[bool], bool | None] | None = None


# Binary sensor entity descriptions for Home Assistant
BINARY_SENSOR_ENTITY_DESCRIPTIONS: tuple[SolakonBinarySensorEntityDescription, ...] = (
    SolakonBinarySensorEntityDescription(
        key="grid_status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda val: not val,
    ),
    SolakonBinarySensorEntityDescription(
        key="island_mode",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        data_key="grid_status",
    ),
)


async def async_setup_entry(
    _: HomeAssistant,
    config_entry: SolakonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solakon ONE sensor entities."""
    # Get device info for all binary sensors
    device_info = await config_entry.runtime_data.hub.async_get_device_info()

    entities: list[SolakonBinarySensor] = []
    entities.extend(
        SolakonBinarySensor(
            config_entry,
            device_info,
            description,
        )
        for description in BINARY_SENSOR_ENTITY_DESCRIPTIONS
    )
    if entities:
        async_add_entities(entities, True)


class SolakonBinarySensor(SolakonEntity, BinarySensorEntity):
    """Representation of a Solakon ONE binary sensor."""

    def __init__(
        self,
        config_entry: SolakonConfigEntry,
        device_info: dict,
        description: SolakonBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(config_entry, device_info, description.key)
        # Set entity description
        self.entity_description = description
        # Set entity ID
        self.entity_id = f"binary_sensor.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        key = (
            self.entity_description.data_key
            if self.entity_description.data_key
            else self.entity_description.key
        )

        if self.coordinator.data and key in self.coordinator.data:
            value = self.coordinator.data[key]
            if self.entity_description.value_fn and value is not None:
                self._attr_is_on = self.entity_description.value_fn(value)
            else:
                self._attr_is_on = value
        else:
            self._attr_is_on = None

        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self._attr_is_on is not None
