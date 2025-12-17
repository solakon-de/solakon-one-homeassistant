"""Select platform for Solakon ONE integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import REGISTERS
from .entity import SolakonEntity
from .remote_control import mode_to_register_value, register_value_to_mode, RemoteControlMode
from .types import SolakonConfigEntry

_LOGGER = logging.getLogger(__name__)

    # "work_mode": {
    #     "name": "Work Mode Control",
    #     "icon": "mdi:cog",
    #     "options": {
    #         1: "Self Use",
    #         2: "Feedin Priority",
    #         3: "Backup",
    #         4: "Peak Shaving",
    #         6: "Force Charge",
    #         7: "Force Discharge",
    #     },
    # },

# Select entity definitions for Home Assistant
SELECT_ENTITY_DESCRIPTIONS: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription(
        key="eps_output",
        options=[
          "0", # Disable
          "2", # EPS Mode
          "3", # UPS Mode
        ],
    ),
)

FORCE_MODE_SELECT_ENTITY_DESCRIPTION = SelectEntityDescription(
    key="force_mode",
    options=[
        "0", # Disabled
        "1", # Force Discharge
        "3", # Force Charge
    ],
)

REMOTE_CONTROLL_MODE_SELECT_ENTITY_DESCRIPTION = SelectEntityDescription(
    key="remote_control_mode",
    options=[
        "0", # Disabled
        "1", # INV Discharge (PV Priority)
        "3", # INV Charge (PV Priority)
        "5", # Battery Discharge
        "7", # Battery Charge
        "9", # Grid Discharge
        "11", # Grid Charge
        "13", # INV Discharge (AC First)
        "15", # INV Charge (AC First)
    ],
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SolakonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solakon ONE select entities."""
    hub = config_entry.runtime_data.hub

    # Get device info
    device_info = await hub.async_get_device_info()

    entities = []

    entities.extend(
        SolakonSelect(
            config_entry,
            device_info,
            description,
        )
        for description in SELECT_ENTITY_DESCRIPTIONS
        # Only create select entities for registers that exist and have rw flag
        if description.key in REGISTERS and REGISTERS[description.key].get("rw", False)
    )
    # Special handling for remote_control_mode (virtual entity)
    entities.append(
        RemoteControlModeSelect(
            config_entry,
            device_info,
            REMOTE_CONTROLL_MODE_SELECT_ENTITY_DESCRIPTION,
        )
    )
    # Special handling for force_mode (virtual entity)
    entities.append(
        ForceModeSelect(
            config_entry,
            device_info,
            FORCE_MODE_SELECT_ENTITY_DESCRIPTION,
        )
    )

    if entities:
        async_add_entities(entities, True)


class SolakonSelect(SolakonEntity, SelectEntity):
    """Representation of a Solakon ONE select entity."""

    def __init__(
        self,
        config_entry: SolakonConfigEntry,
        device_info: dict,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(config_entry, device_info, description.key)
        self._register_config = REGISTERS[description.key]

        self.entity_description = description

        # Set entity ID
        self.entity_id = f"select.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and self.entity_description.key in self.coordinator.data:
            raw_value = self.coordinator.data[self.entity_description.key]

            # raw_value is already processed by modbus.py (scaled if needed)
            # For selects, it should be an integer
            if isinstance(raw_value, (int, float)):
                str_value = f"{int(raw_value)}"

                # Convert numeric value to string option
                if str_value in self.entity_description.options:
                    self._attr_current_option = str_value
                    _LOGGER.debug(
                        f"{self.entity_description.key}: raw_value={raw_value}, mapped to '{self._attr_current_option}'"
                    )
                else:
                    _LOGGER.warning(
                        f"Unknown value {str_value} for {self.entity_description.key}. "
                        f"Valid options: {self.entity_description.options}"
                    )
                    self._attr_current_option = None
            else:
                _LOGGER.warning(
                    f"Invalid value type for {self.entity_description.key}: {type(raw_value)}"
                )
                self._attr_current_option = None
        else:
            self._attr_current_option = None

        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self.entity_description.options:
            _LOGGER.error(
                f"Invalid option '{option}' for {self.entity_description.key}. "
                f"Valid options: {self.entity_description.options}"
            )
            return

        # Get the numeric value to write
        numeric_value = int(option)
        address = self._register_config["address"]

        _LOGGER.info(
            f"Setting {self.entity_description.key} at address {address} to '{option}' (value: {numeric_value})"
        )

        # Write the value to the register (single register for selects)
        success = await self._config_entry.runtime_data.hub.async_write_register(address, numeric_value)

        if success:
            _LOGGER.info(f"Successfully set {self.entity_description.key} to '{option}'")
            # Update the state immediately (optimistic update)
            self._attr_current_option = option
            self.async_write_ha_state()
            # Request coordinator to refresh data to confirm the change
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error(f"Failed to set {self.entity_description.key} to '{option}'")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Entity is available if coordinator succeeded and we have a valid value
        return self.coordinator.last_update_success


class RemoteControlModeSelect(SolakonEntity, SelectEntity):
    """Special select entity for Remote Control Mode.

    This entity translates between user-friendly mode names and the
    bitfield register value for register 46001 (remote_control).
    """

    def __init__(
        self,
        config_entry: SolakonConfigEntry,
        device_info: dict,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the remote control mode select entity."""
        super().__init__(config_entry, device_info, description.key)
        self._register_key = "remote_control"
        self._register_config = REGISTERS[self._register_key]

        self.entity_description = description

        # Set entity ID
        self.entity_id = f"select.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and self._register_key in self.coordinator.data:
            raw_value = self.coordinator.data[self._register_key]

            if isinstance(raw_value, (int, float)):
                register_value = int(raw_value)

                # Convert register value to mode
                mode = register_value_to_mode(register_value)
                str_value = f"{int(mode)}"

                # Convert mode value to string option
                if str_value in self.entity_description.options:
                    self._attr_current_option = str_value
                    _LOGGER.debug(
                        f"Remote control mode: register={register_value:#06x}, "
                        f"mode={mode.name}, option='{self._attr_current_option}'"
                    )
                else:
                    _LOGGER.warning(
                        f"Unknown remote control mode value {str_value}. "
                        f"Valid modes: {self.entity_description.options}"
                    )
                    self._attr_current_option = None
            else:
                _LOGGER.warning(
                    f"Invalid value type for remote_control: {type(raw_value)}"
                )
                self._attr_current_option = None
        else:
            self._attr_current_option = None

        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self.entity_description.options:
            _LOGGER.error(
                f"Invalid option '{option}' for remote_control_mode. "
                f"Valid options: {self.entity_description.options}"
            )
            return

        # Get the mode enum value
        mode_value = int(option)
        mode = RemoteControlMode(mode_value)

        # Convert mode to register value
        register_value = mode_to_register_value(mode)

        # Get the register address for remote_control
        address = self._register_config["address"]

        _LOGGER.info(
            f"Setting remote_control_mode to '{option}' "
            f"(mode={mode.name}, register value={register_value:#06x}) "
            f"at address {address}"
        )

        # Write the value to the register
        success = await self._config_entry.runtime_data.hub.async_write_register(address, register_value)

        if success:
            _LOGGER.info(f"Successfully set remote_control_mode to '{option}'")
            # Update the state immediately (optimistic update)
            self._attr_current_option = option
            self.async_write_ha_state()
            # Request coordinator to refresh data to confirm the change
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error(f"Failed to set remote_control_mode to '{option}'")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class ForceModeSelect(SolakonEntity, SelectEntity):
    """Special select entity for Force Mode (Force Charge/Discharge).

    This entity provides a simplified interface for force charging/discharging
    by controlling register 46001 (remote_control) with predefined values.
    """

    def __init__(
        self,
        config_entry: SolakonConfigEntry,
        device_info: dict,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the force mode select entity."""
        super().__init__(config_entry, device_info, description.key)
        self._register_key = "remote_control"
        self._register_config = REGISTERS[self._register_key]

        self.entity_description = description

        # Set entity ID
        self.entity_id = "select.solakon_one_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data and self._register_key in self.coordinator.data:
            raw_value = self.coordinator.data[self._register_key]

            if isinstance(raw_value, (int, float)):
                register_value = int(raw_value)

                # Check if the value matches one of our force modes
                # Force modes: 0 (disabled), 1 (force discharge), 3 (force charge)
                mode_value = register_value & 0b1111  # Lower 4 bits
                str_value = f"{mode_value}"

                if str_value in self.entity_description.options:
                    self._attr_current_option = str_value
                    _LOGGER.debug(
                        f"Force mode: register={register_value:#06x}, "
                        f"mode={str_value}, option='{self._attr_current_option}'"
                    )
                else:
                    # Not a force mode (could be other remote control mode)
                    self._attr_current_option = self.entity_description.options[0]  # Default to "Disabled"
                    _LOGGER.debug(
                        f"Force mode: register={register_value:#06x} not a force mode, showing as Disabled"
                    )
            else:
                _LOGGER.warning(
                    f"Invalid value type for remote_control: {type(raw_value)}"
                )
                self._attr_current_option = None
        else:
            self._attr_current_option = None

        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self.entity_description.options:
            _LOGGER.error(
                f"Invalid option '{option}' for force_mode. "
                f"Valid options: {self.entity_description.options}"
            )
            return

        # Get the mode value (0, 1, or 3)
        mode_value = int(option)

        # Get the register address for remote_control
        address = self._register_config["address"]

        _LOGGER.info(
            f"Setting force_mode to '{option}' "
            f"(register value={mode_value:#06x}) at address {address}"
        )

        # Write the value to the register
        success = await self._config_entry.runtime_data.hub.async_write_register(address, mode_value)

        if success:
            _LOGGER.info(f"Successfully set force_mode to '{option}'")
            # Update the state immediately (optimistic update)
            self._attr_current_option = option
            self.async_write_ha_state()
            # Request coordinator to refresh data to confirm the change
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error(f"Failed to set force_mode to '{option}'")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
