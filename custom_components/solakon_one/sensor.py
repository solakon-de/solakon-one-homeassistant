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

# Sensor entity descriptions for Home Assistant
SENSOR_ENTITY_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="bms1_soh",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="pv1_power",
        translation_key="pvn_power",
        translation_placeholder={"n": "1"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SensorEntityDescription(
        key="pv2_power",
        translation_key="pvn_power",
        translation_placeholder={"n": "2"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SensorEntityDescription(
        key="pv3_power",
        translation_key="pvn_power",
        translation_placeholder={"n": "3"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SensorEntityDescription(
        key="pv4_power",
        translation_key="pvn_power",
        translation_placeholder={"n": "4"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SensorEntityDescription(
        key="total_pv_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SensorEntityDescription(
        key="active_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SensorEntityDescription(
        key="reactive_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.REACTIVE_POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfReactivePower.KILO_VOLT_AMPERE_REACTIVE,
    ),
    SensorEntityDescription(
        key="battery_combined_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SensorEntityDescription(
        key="battery_total_charge_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="battery_total_discharge_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="battery_soc",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="eps_power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    SensorEntityDescription(
        key="pv1_voltage",
        translation_key="pvn_voltage",
        translation_placeholder={"n": "1"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SensorEntityDescription(
        key="pv2_voltage",
        translation_key="pvn_voltage",
        translation_placeholder={"n": "2"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SensorEntityDescription(
        key="pv3_voltage",
        translation_key="pvn_voltage",
        translation_placeholder={"n": "3"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SensorEntityDescription(
        key="pv4_voltage",
        translation_key="pvn_voltage",
        translation_placeholder={"n": "4"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SensorEntityDescription(
        key="grid_r_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SensorEntityDescription(
        key="battery1_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SensorEntityDescription(
        key="eps_voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SensorEntityDescription(
        key="pv1_current",
        translation_key="pvn_current",
        translation_placeholder={"n": "1"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SensorEntityDescription(
        key="pv2_current",
        translation_key="pvn_current",
        translation_placeholder={"n": "2"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SensorEntityDescription(
        key="pv3_current",
        translation_key="pvn_current",
        translation_placeholder={"n": "3"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SensorEntityDescription(
        key="pv4_current",
        translation_key="pvn_current",
        translation_placeholder={"n": "4"},
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SensorEntityDescription(
        key="battery1_current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SensorEntityDescription(
        key="eps_current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SensorEntityDescription(
        key="pv_total_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="cumulative_generation",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="daily_generation",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="internal_temp",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="bms1_ambient_temp",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="bms1_design_energy",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=2,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="bms1_max_temp",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="bms1_min_temp",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="power_factor",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER_FACTOR,
    ),
    SensorEntityDescription(
        key="inverter_r_frequency",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
    ),
    SensorEntityDescription(
        key="grid_total_export_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="grid_total_import_energy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="grid_frequency",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
    ),
    SensorEntityDescription(
        key="grid_standard_code",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="network_status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="remote_control",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="remote_timeout_countdown",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="operating_mode",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        options=[0, 1, 2, 3, 4, 6, 7],
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

    entities: list[SolakonSensor] = []
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
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, device_info, description.key)
        # Set entity description
        self.entity_description = description
        # Set entity ID
        self.entity_id = f"sensor.solakon_one_{description.key}"
        # Prioritize translation key from entity description
        if self.entity_description.translation_key is not None:
            self._attr_translation_key = self.entity_description.translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if (
            self.coordinator.data
            and self.entity_description.key in self.coordinator.data
        ):
            self._attr_native_value = self.coordinator.data[self.entity_description.key]
        else:
            self._attr_native_value = None

        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success and self._attr_native_value is not None
        )
