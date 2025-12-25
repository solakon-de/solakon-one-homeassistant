"""Sensor platform for Solakon ONE integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import SolakonEntity
from .types import SolakonConfigEntry

_LOGGER = logging.getLogger(__name__)


def invert_value(value):
    """Invert a numeric value.

    - For int/float: return -value
    - For numeric strings: try to parse to float and invert
    - Otherwise return the value unchanged
    """
    try:
        if isinstance(value, (int, float)):
            return -value
        if isinstance(value, str):
            # try parse numeric string
            try:
                num = float(value)
            except ValueError:
                return value
            # preserve integerness if applicable
            if num.is_integer():
                return int(-num)
            return -num
    except Exception:
        return value
    return value

    # Control Status Sensors (showing current values of controllable parameters)
    # "export_power_limit": {
    #     "name": "Export Power Limit",
    #     "device_class": "power",
    #     "state_class": "measurement",
    #     "unit": "W",
    #     "icon": "mdi:transmission-tower-export",
    # },
    # "import_power_limit": {
    #     "name": "Import Power Limit",
    #     "device_class": "power",
    #     "state_class": "measurement",
    #     "unit": "W",
    #     "icon": "mdi:transmission-tower-import",
    # },
    # "export_peak_limit": {
    #     "name": "Export Peak Limit",
    #     "device_class": "power",
    #     "state_class": "measurement",
    #     "unit": "W",
    #     "icon": "mdi:transmission-tower-export",
    # },
    # "work_mode": {
    #     "name": "Work Mode",
    #     "icon": "mdi:cog",
    # },

class SolakonSensorEntityDescription(SensorEntityDescription):
    """Extends SolakonSensorEntityDescription to add an invert option."""

    invert: bool = False

# Sensor entity descriptions for Home Assistant
SENSOR_ENTITY_DESCRIPTIONS: tuple[SolakonSensorEntityDescription, ...] = (
    SolakonSensorEntityDescription(
        key="bms1_soh",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SolakonSensorEntityDescription(
        key="pv1_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SolakonSensorEntityDescription(
        key="pv2_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SolakonSensorEntityDescription(
        key="pv3_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SolakonSensorEntityDescription(
        key="pv4_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SolakonSensorEntityDescription(
        key="total_pv_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SolakonSensorEntityDescription(
        key="active_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SolakonSensorEntityDescription(
        key="reactive_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.REACTIVE_POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfReactivePower.KILO_VOLT_AMPERE_REACTIVE,
    ),
    SolakonSensorEntityDescription(
        key="battery_combined_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        invert=True,
    ),
    SolakonSensorEntityDescription(
        key="battery_total_charge_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SolakonSensorEntityDescription(
        key="battery_total_discharge_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SolakonSensorEntityDescription(
        key="battery_soc",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SolakonSensorEntityDescription(
        key="eps_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SolakonSensorEntityDescription(
        key="pv1_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SolakonSensorEntityDescription(
        key="pv2_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SolakonSensorEntityDescription(
        key="pv3_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SolakonSensorEntityDescription(
        key="pv4_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SolakonSensorEntityDescription(
        key="grid_r_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SolakonSensorEntityDescription(
        key="battery1_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SolakonSensorEntityDescription(
        key="eps_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SolakonSensorEntityDescription(
        key="pv1_current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SolakonSensorEntityDescription(
        key="pv2_current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SolakonSensorEntityDescription(
        key="pv3_current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SolakonSensorEntityDescription(
        key="pv4_current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SolakonSensorEntityDescription(
        key="battery1_current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SolakonSensorEntityDescription(
        key="eps_current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SolakonSensorEntityDescription(
        key="pv_total_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SolakonSensorEntityDescription(
        key="cumulative_generation",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SolakonSensorEntityDescription(
        key="daily_generation",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SolakonSensorEntityDescription(
        key="internal_temp",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SolakonSensorEntityDescription(
        key="bms1_ambient_temp",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SolakonSensorEntityDescription(
        key="bms1_design_energy",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=2,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SolakonSensorEntityDescription(
        key="bms1_max_temp",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SolakonSensorEntityDescription(
        key="bms1_min_temp",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SolakonSensorEntityDescription(
        key="power_factor",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER_FACTOR,
    ),
    SolakonSensorEntityDescription(
        key="inverter_r_frequency",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
    ),
    SolakonSensorEntityDescription(
        key="grid_total_export_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SolakonSensorEntityDescription(
        key="grid_total_import_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SolakonSensorEntityDescription(
        key="grid_frequency",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
    ),
    SolakonSensorEntityDescription(
        key="grid_standard_code",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SolakonSensorEntityDescription(
        key="network_status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SolakonSensorEntityDescription(
        key="remote_control",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SolakonSensorEntityDescription(
        key="remote_timeout_countdown",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_display_precision=0,
    ),
    SolakonSensorEntityDescription(
        key="operating_mode",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        options=[1, 2, 3, 4, 6, 7],
    ),
)

async def async_setup_entry(
    _: HomeAssistant,
    config_entry: SolakonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solakon ONE sensor entities."""
    # Get device info for all sensors
    device_info = await config_entry.runtime_data.hub.async_get_device_info()

    entities = []
    entities.extend(
        SolakonSensor(
            config_entry,
            device_info,
            description,
        )
        for description in SENSOR_ENTITY_DESCRIPTIONS
    )
    if entities:
        async_add_entities(entities, True)


class SolakonSensor(SolakonEntity, SensorEntity):
    """Representation of a Solakon ONE sensor."""

    def __init__(
        self,
        config_entry: SolakonConfigEntry,
        device_info: dict,
        description: SolakonSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, device_info, description.key)
        # Set entity description
        self.entity_description = description
        # Set entity ID
        self.entity_id = f"sensor.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and self.entity_description.key in self.coordinator.data:
            value = self.coordinator.data[self.entity_description.key]

            # Apply optional description-level transforms
            try:
                # boolean `invert` attribute convenience
                if getattr(self.entity_description, "invert", False):
                    value = invert_value(value)

                # `value_fn` callable on the description to transform the raw value
                value_fn = getattr(self.entity_description, "value_fn", None)
                if callable(value_fn):
                    value = value_fn(value)
            except Exception as err:  # guard against faulty user-provided transforms
                _LOGGER.warning(
                    "Error applying value transform for %s: %s",
                    self.entity_description.key,
                    err,
                )

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
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self._attr_native_value is not None
