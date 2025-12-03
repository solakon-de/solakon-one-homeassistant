"""Sensor platform for Solakon ONE integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DEFINITIONS

_LOGGER = logging.getLogger(__name__)


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


class SolakonSensor(CoordinatorEntity, SensorEntity):
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
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._definition = definition
        self._config_entry = config_entry
        self._device_info = device_info
        
        # Set unique ID and entity ID
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_key}"
        self.entity_id = f"sensor.solakon_one_{sensor_key}"
        
        # Set basic attributes
        self._attr_name = definition["name"]
        self._attr_icon = definition.get("icon")
        
        # Set device class
        if "device_class" in definition:
            device_class = definition["device_class"]
            if device_class == "power":
                self._attr_device_class = SensorDeviceClass.POWER
            elif device_class == "energy":
                self._attr_device_class = SensorDeviceClass.ENERGY
            elif device_class == "voltage":
                self._attr_device_class = SensorDeviceClass.VOLTAGE
            elif device_class == "current":
                self._attr_device_class = SensorDeviceClass.CURRENT
            elif device_class == "temperature":
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
            elif device_class == "frequency":
                self._attr_device_class = SensorDeviceClass.FREQUENCY
            elif device_class == "battery":
                self._attr_device_class = SensorDeviceClass.BATTERY
            elif device_class == "power_factor":
                self._attr_device_class = SensorDeviceClass.POWER_FACTOR
            elif device_class == "reactive_power":
                self._attr_device_class = SensorDeviceClass.REACTIVE_POWER
            elif device_class == "duration":
                self._attr_device_class = SensorDeviceClass.DURATION
        
        # Set state class
        if "state_class" in definition:
            state_class = definition["state_class"]
            if state_class == "measurement":
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif state_class == "total_increasing":
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        
        # Set unit of measurement
        unit = definition.get("unit")
        if unit == "kW":
            self._attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
        elif unit == "W":
            self._attr_native_unit_of_measurement = UnitOfPower.WATT
        elif unit == "kWh":
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        elif unit == "V":
            self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        elif unit == "A":
            self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        elif unit == "Hz":
            self._attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
        elif unit == "°C":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif unit == "%":
            self._attr_native_unit_of_measurement = PERCENTAGE
        elif unit == "kvar":
            self._attr_native_unit_of_measurement = "kvar"
        elif unit == "var":
            self._attr_native_unit_of_measurement = "var"
        elif unit == "s":
            self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        elif unit:
            self._attr_native_unit_of_measurement = unit

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=self._config_entry.data.get("name", "Solakon ONE"),
            manufacturer=self._device_info.get("manufacturer", "Solakon"),
            model=self._device_info.get("model", "One"),
            sw_version=self._device_info.get("version"),
            serial_number=self._device_info.get("serial"),
        )

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