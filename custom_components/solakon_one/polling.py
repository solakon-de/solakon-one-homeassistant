"""Register keys the hub polls for the entities of a config entry."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .binary_sensor import (
    BINARY_SENSOR_ENTITY_DESCRIPTIONS,
    SolakonBinarySensorEntityDescription,
)
from .const import REGISTERS
from .number import NUMBER_ENTITY_DESCRIPTIONS
from .select import SELECT_ENTITY_DESCRIPTIONS
from .sensor import SENSOR_ENTITY_DESCRIPTIONS, SolakonSensorEntityDescription
from .types import SolakonConfigEntry

# Registers read by number and select entities; the remote control and force
# mode selects read register remote_control.
CONTROL_KEYS = {
    d.key
    for d in (*NUMBER_ENTITY_DESCRIPTIONS, *SELECT_ENTITY_DESCRIPTIONS)
    if d.key in REGISTERS
} | {"remote_control"}


def polled_keys(hass: HomeAssistant, entry: SolakonConfigEntry) -> set[str]:
    """Return the registers of control entities plus those of enabled sensors.

    Sensors without a registry entry yet count as enabled if they are enabled
    by default. Enabling a sensor later reloads the config entry, which
    recomputes the keys.
    """
    registry = er.async_get(hass)
    registered = {
        e.unique_id: e.disabled_by is None
        for e in er.async_entries_for_config_entry(registry, entry.entry_id)
    }
    keys = set(CONTROL_KEYS)
    descriptions: tuple[
        SolakonSensorEntityDescription | SolakonBinarySensorEntityDescription, ...
    ] = (*SENSOR_ENTITY_DESCRIPTIONS, *BINARY_SENSOR_ENTITY_DESCRIPTIONS)
    for description in descriptions:
        enabled = registered.get(
            f"{entry.entry_id}_{description.key}",
            description.entity_registry_enabled_default,
        )
        if enabled:
            keys.add(description.data_key or description.key)
    return keys
