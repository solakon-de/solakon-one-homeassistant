"""Sensor platform for Solakon ONE integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_DEFINITIONS, UOM_MAPPING
from .entity import SolakonEntity

_LOGGER = logging.getLogger(__name__)

DEVICE_CLASS_MAPPING = {
    "power": SensorDeviceClass.POWER,
    "energy": SensorDeviceClass.ENERGY,
    "voltage": SensorDeviceClass.VOLTAGE,
    "current": SensorDeviceClass.CURRENT,
    "temperature": SensorDeviceClass.TEMPERATURE,
    "frequency": SensorDeviceClass.FREQUENCY,
    "battery": SensorDeviceClass.BATTERY,
    "power_factor": SensorDeviceClass.POWER_FACTOR,
    "reactive_power": SensorDeviceClass.REACTIVE_POWER,
    "duration": SensorDeviceClass.DURATION,
}

STATE_CLASS_MAPPING = {
    "measurement": SensorStateClass.MEASUREMENT,
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solakon ONE sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    hub = hass.data[DOMAIN][config_entry.entry_id]["hub"]

    # Get device info for all sensors
    device_info = await hub.async_get_device_info()
    
    entities = []
    for key, definition in SENSOR_DEFINITIONS.items():
        entities.append(
            SolakonSensor(
                coordinator,
                config_entry,
                key,
                definition,
                device_info,
            )
        )

    async_add_entities(entities, True)


class SolakonSensor(SolakonEntity, SensorEntity):
    """Representation of a Solakon ONE sensor."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        sensor_key: str,
        definition: dict,
        device_info: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry, device_info, definition, sensor_key)
        self._sensor_key = sensor_key
        # Set entity ID
        self.entity_id = f"sensor.solakon_one_{sensor_key}"
        
        category = definition.get("entity_category", None)
        if category == "diagnostic":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        elif category == "config":
            self._attr_entity_category = EntityCategory.CONFIG

        # Set device class
        if "device_class" in definition:
            device_class = definition["device_class"]
            self._attr_device_class = DEVICE_CLASS_MAPPING.get(device_class) if device_class in DEVICE_CLASS_MAPPING else None

        # Set state class
        if "state_class" in definition:
            state_class = definition["state_class"]
            self._attr_state_class = STATE_CLASS_MAPPING.get(state_class) if state_class in STATE_CLASS_MAPPING else None
        
        # Set unit of measurement
        if "unit" in definition:
            unit = definition["unit"]
            self._attr_native_unit_of_measurement = UOM_MAPPING.get(unit) if unit in UOM_MAPPING else unit

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and self._sensor_key in self.coordinator.data:
            value = self.coordinator.data[self._sensor_key]
            
            # Handle special cases
            if isinstance(value, dict):
                # For bitfield/status values, extract meaningful data
                if "operation" in value:
                    self._attr_native_value = "Operating" if value["operation"] else "Standby"
                elif "fault" in value:
                    self._attr_native_value = "Fault" if value["fault"] else "Normal"
                else:
                    self._attr_native_value = str(value)
            else:
                self._attr_native_value = value
                
            # Add extra state attributes for complex values
            if isinstance(value, dict):
                self._attr_extra_state_attributes = value
            else:
                self._attr_extra_state_attributes = {}
        else:
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}
        
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        # battery soc sensor
        if self._sensor_key == "battery_soc":
            try:
                soc = int(self.native_value)
            except (ValueError, TypeError):
                return "mdi:battery-unknown"

            if soc > 90:
                return "mdi:battery"
            
            rounded_soc = (soc + 5) // 10 * 10
            if rounded_soc == 0:
                return "mdi:battery-outline"
            
            return f"mdi:battery-{rounded_soc}"
        
        # For all other sensors return the static icon defined in const.py
        return self._definition.get("icon")


    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self._attr_native_value is not None