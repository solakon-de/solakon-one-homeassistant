"""Number platform for Solakon ONE integration."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode, NumberDeviceClass, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, REGISTERS
from .entity import SolakonEntity

_LOGGER = logging.getLogger(__name__)


    # "export_power_limit": {
    #     "name": "Export Power Limit Control",
    #     "icon": "mdi:transmission-tower-export",
    #     "min": 0,
    #     "max": 100000,  # 100kW max, will be adjusted based on inverter Pmax
    #     "step": 100,
    #     "unit": "W",
    #     "device_class": "power",
    #     "mode": "box",
    # },
    # "import_power_limit": {
    #     "name": "Import Power Limit Control",
    #     "icon": "mdi:transmission-tower-import",
    #     "min": 0,
    #     "max": 100000,  # 100kW max
    #     "step": 100,
    #     "unit": "W",
    #     "device_class": "power",
    #     "mode": "box",
    # },
    # "export_peak_limit": {
    #     "name": "Export Peak Limit Control",
    #     "icon": "mdi:transmission-tower-export",
    #     "min": 0,
    #     "max": 100000,  # 100kW max
    #     "step": 100,
    #     "unit": "W",
    #     "device_class": "power",
    #     "mode": "box",
    # },

# Number entity descriptions for Home Assistant
NUMBER_ENTITY_DESCRIPTIONS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="minimum_soc",
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
    ),
    NumberEntityDescription(
        key="maximum_soc",
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
    ),
    NumberEntityDescription(
        key="minimum_soc_ongrid",
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
    ),
    NumberEntityDescription(
        key="battery_max_charge_current",
        mode=NumberMode.BOX,
        device_class=NumberDeviceClass.CURRENT,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        native_min_value=0,
        native_max_value=40,
        native_step=1,
        entity_registry_enabled_default=False,
    ),
    NumberEntityDescription(
        key="battery_max_discharge_current",
        mode=NumberMode.BOX,
        device_class=NumberDeviceClass.CURRENT,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        native_min_value=0,
        native_max_value=40,
        native_step=1,
        entity_registry_enabled_default=False,
    ),
    NumberEntityDescription(
        key="remote_active_power",
        mode=NumberMode.BOX,
        device_class=NumberDeviceClass.POWER,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfPower.WATT,
        native_min_value=-100000, # -100kW (charging/import)
        native_max_value=100000,  # +100kW (discharging/export)
        native_step=100,
    ),
    NumberEntityDescription(
        key="remote_reactive_power",
        mode=NumberMode.BOX,
        device_class=NumberDeviceClass.REACTIVE_POWER,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
        native_min_value=-100000,
        native_max_value=100000,
        native_step=100,
    ),
    NumberEntityDescription(
        key="remote_timeout_set",
        mode=NumberMode.BOX,
        device_class=NumberDeviceClass.DURATION,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=3600,
        native_step=10,
    ),
)

FORCE_DURATION_NUMBER_ENTITY_DESCRIPTION = NumberEntityDescription(
    key="force_duration",
    mode=NumberMode.SLIDER,
    device_class=NumberDeviceClass.DURATION,
    entity_category=EntityCategory.CONFIG,
    native_unit_of_measurement=UnitOfTime.MINUTES,
    native_min_value=0,
    native_max_value=1092,  # 65535 seconds = ~1092 minutes
    native_step=1,
)

FORCE_POWER_NUMBER_ENTITY_DESCRIPTION = NumberEntityDescription(
    key="force_power",
    mode=NumberMode.BOX,
    device_class=NumberDeviceClass.POWER,
    entity_category=EntityCategory.CONFIG,
    native_unit_of_measurement=UnitOfPower.WATT,
    native_min_value=0,
    native_max_value=1200,  # Will be validated based on mode (1200W charge, 800W discharge)
    native_step=10,
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solakon ONE number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    hub = hass.data[DOMAIN][config_entry.entry_id]["hub"]

    # Get device info
    device_info = await hub.async_get_device_info()

    entities = []

    entities.extend(
        SolakonNumber(
            coordinator,
            hub,
            config_entry,
            device_info,
            description,
        )
        for description in NUMBER_ENTITY_DESCRIPTIONS
        # Only create number entities for registers that exist and have rw flag
        if description.key in REGISTERS and REGISTERS[description.key].get("rw", False)
    )
    # Special handling for force_duration (virtual entity with minutes<->seconds conversion)
    entities.append(
        ForceDurationNumber(
            coordinator,
            hub,
            config_entry,
            device_info,
            FORCE_DURATION_NUMBER_ENTITY_DESCRIPTION,
        )
    )
    # Special handling for force_power (writes to both 46003 and 46005)
    entities.append(
        ForcePowerNumber(
            coordinator,
            hub,
            config_entry,
            device_info,
            FORCE_POWER_NUMBER_ENTITY_DESCRIPTION,
        )
    )

    if entities:
        async_add_entities(entities, True)


class SolakonNumber(SolakonEntity, NumberEntity):
    """Representation of a Solakon ONE number entity."""

    def __init__(
        self,
        coordinator,
        hub,
        config_entry: ConfigEntry,
        device_info: dict,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, config_entry, device_info, description.key)
        self._hub = hub
        self._number_key = description.key
        self._register_config = REGISTERS[description.key]

        self.entity_description = description

        # Set entity ID
        self.entity_id = f"number.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and self._number_key in self.coordinator.data:
            value = self.coordinator.data[self._number_key]

            # Value is already processed by modbus.py (scaled and converted)
            if isinstance(value, (int, float)):
                self._attr_native_value = float(value)
                _LOGGER.debug(
                    f"{self._number_key}: Read value = {self._attr_native_value}"
                )
            else:
                _LOGGER.warning(
                    f"Invalid value type for {self._number_key}: {type(value)}"
                )
                self._attr_native_value = None
        else:
            self._attr_native_value = None

        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Convert to int for Modbus register writing
        int_value = int(value)

        # Get register info
        address = self._register_config["address"]
        count = self._register_config.get("count", 1)
        data_type = self._register_config.get("type", "u16")
        scale = self._register_config.get("scale", 1)

        # Apply scaling for write (reverse of read scaling)
        # If scale=1 (which is the case for all our RW registers), this does nothing
        if scale != 1:
            int_value = int(value * scale)

        _LOGGER.info(
            f"Setting {self._number_key} at address {address} to {value} "
            f"(raw value: {int_value}, type: {data_type}, count: {count})"
        )

        # Write based on register count
        if count == 1:
            # Single register write (16-bit)
            # Ensure value fits in uint16 range
            if int_value < 0:
                int_value = 0
            elif int_value > 0xFFFF:
                int_value = 0xFFFF

            success = await self._hub.async_write_register(address, int_value)
        else:
            # Multi-register write (32-bit)
            # Handle signed/unsigned conversion
            if "i32" in data_type.lower() and int_value < 0:
                # Convert negative to two's complement for I32
                int_value = int_value + 0x100000000

            # Ensure value fits in uint32 range
            if int_value < 0:
                int_value = 0
            elif int_value > 0xFFFFFFFF:
                int_value = 0xFFFFFFFF

            # Split into high and low words (big-endian: high word first)
            high_word = (int_value >> 16) & 0xFFFF
            low_word = int_value & 0xFFFF
            values = [high_word, low_word]

            _LOGGER.debug(
                f"Writing 32-bit value: {int_value:#x} = [{high_word:#x}, {low_word:#x}]"
            )

            success = await self._hub.async_write_registers(address, values)

        if success:
            _LOGGER.info(f"Successfully set {self._number_key} to {value}")
            # Update the state immediately (optimistic update)
            self._attr_native_value = float(value)
            self.async_write_ha_state()
            # Request coordinator to refresh data to confirm the change
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error(f"Failed to set {self._number_key} to {value}")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Entity is available if coordinator succeeded
        return self.coordinator.last_update_success


class ForceDurationNumber(SolakonEntity, NumberEntity):
    """Number entity for Force Mode Duration with minutes<->seconds conversion.

    This entity controls register 46002 (remote_timeout_set) but displays
    the value in minutes for better user experience, while storing it in
    seconds in the register.
    """

    def __init__(
        self,
        coordinator,
        hub,
        config_entry: ConfigEntry,
        device_info: dict,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the force duration number entity."""
        super().__init__(coordinator, config_entry, device_info, description.key)
        self._hub = hub

        self.entity_description = description

        # Set entity ID
        self.entity_id = f"number.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and "remote_timeout_set" in self.coordinator.data:
            value_seconds = self.coordinator.data["remote_timeout_set"]

            # Convert from seconds to minutes for display
            if isinstance(value_seconds, (int, float)):
                value_minutes = float(value_seconds) / 60.0
                self._attr_native_value = round(value_minutes, 1)  # Round to 1 decimal place
                _LOGGER.debug(
                    f"force_duration: Read value = {value_seconds}s = {self._attr_native_value} min"
                )
            else:
                _LOGGER.warning(
                    f"Invalid value type for remote_timeout_set: {type(value_seconds)}"
                )
                self._attr_native_value = None
        else:
            self._attr_native_value = None

        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Convert from minutes to seconds for writing
        value_seconds = int(value * 60)

        # Ensure value fits in uint16 range (0-65535)
        if value_seconds < 0:
            value_seconds = 0
        elif value_seconds > 65535:
            value_seconds = 65535

        address = REGISTERS["remote_timeout_set"]["address"]

        _LOGGER.info(
            f"Setting force_duration to {value} min (raw value: {value_seconds}s) at address {address}"
        )

        # Write to register 46002
        success = await self._hub.async_write_register(address, value_seconds)

        if success:
            _LOGGER.info(f"Successfully set force_duration to {value} min ({value_seconds}s)")
            # Update the state immediately (optimistic update)
            self._attr_native_value = float(value)
            self.async_write_ha_state()
            # Request coordinator to refresh data to confirm the change
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error(f"Failed to set force_duration to {value} min")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class ForcePowerNumber(SolakonEntity, NumberEntity):
    """Number entity for Force Mode Power.

    This entity controls both registers 46003 (remote_active_power) and
    46005 (remote_reactive_power), ensuring they always have the same
    positive value as required by the force charge/discharge operation.
    """

    def __init__(
        self,
        coordinator,
        hub,
        config_entry: ConfigEntry,
        device_info: dict,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the force power number entity."""
        super().__init__(coordinator, config_entry, device_info, description.key)
        self._hub = hub

        self.entity_description = description

        # Set entity ID
        self.entity_id = f"number.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Read from register 46003 (remote_active_power)
        if self.coordinator.data and "remote_active_power" in self.coordinator.data:
            value = self.coordinator.data["remote_active_power"]

            # Always use absolute value (positive)
            if isinstance(value, (int, float)):
                self._attr_native_value = abs(float(value))
                _LOGGER.debug(
                    f"force_power: Read value = {self._attr_native_value}W"
                )
            else:
                _LOGGER.warning(
                    f"Invalid value type for remote_active_power: {type(value)}"
                )
                self._attr_native_value = None
        else:
            self._attr_native_value = None

        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Always use positive value
        int_value = abs(int(value))

        # Validate based on current force mode
        # (You could add validation here to check if force charge is active and limit to 1200W,
        #  or if force discharge is active and limit to 800W)

        address_46003 = REGISTERS["remote_active_power"]["address"]
        address_46005 = REGISTERS["remote_reactive_power"]["address"]

        _LOGGER.info(
            f"Setting force_power to {int_value}W (writing to both 46003 and 46005)"
        )

        # Write to both registers 46003 and 46005 (32-bit values)
        # Split into high and low words (big-endian: high word first)
        high_word = (int_value >> 16) & 0xFFFF
        low_word = int_value & 0xFFFF
        values = [high_word, low_word]

        _LOGGER.debug(
            f"Writing 32-bit value: {int_value:#x} = [{high_word:#x}, {low_word:#x}]"
        )

        # Write to both registers
        success_46003 = await self._hub.async_write_registers(address_46003, values)
        success_46005 = await self._hub.async_write_registers(address_46005, values)

        if success_46003 and success_46005:
            _LOGGER.info(f"Successfully set force_power to {int_value}W")
            # Update the state immediately (optimistic update)
            self._attr_native_value = float(int_value)
            self.async_write_ha_state()
            # Request coordinator to refresh data to confirm the change
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error(
                f"Failed to set force_power to {int_value}W "
                f"(46003: {success_46003}, 46005: {success_46005})"
            )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
