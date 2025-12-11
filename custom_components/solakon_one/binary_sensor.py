"""Binary sensor platform for Solakon ONE integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SolakonEntity

_LOGGER = logging.getLogger(__name__)


# Binary sensor entity descriptions for Home Assistant
BINARY_SENSOR_ENTITY_DESCRIPTIONS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="island_mode",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solakon ONE sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    hub = hass.data[DOMAIN][config_entry.entry_id]["hub"]

    # Get device info for all binary sensors
    device_info = await hub.async_get_device_info()

    entities = []

    entities.extend(
        SolakonSensor(
            coordinator,
            config_entry,
            device_info,
            description,
        )
        for description in BINARY_SENSOR_ENTITY_DESCRIPTIONS
    )

    async_add_entities(entities, True)


class SolakonSensor(SolakonEntity, BinarySensorEntity):
    """Representation of a Solakon ONE binary sensor."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        device_info: dict,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, config_entry, device_info, description.key)
        # Set entity description
        self.entity_description = description
        # Set entity ID
        self.entity_id = f"binary_sensor.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data and self.entity_description.key in self.coordinator.data:
            self._attr_is_on = self.coordinator.data[self.entity_description.key]
        else:
            self._attr_is_on = None

        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self._attr_is_on is not None
