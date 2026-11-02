from custom_components.solakon_one.sensor import (
    OPERATING_MODES,
    SENSOR_ENTITY_DESCRIPTIONS,
)


def test_operating_mode_sensor_maps_register_values_to_options() -> None:
    description = next(
        d for d in SENSOR_ENTITY_DESCRIPTIONS if d.key == "operating_mode"
    )

    assert description.options == OPERATING_MODES
    assert description.value_fn is not None
    assert description.value_fn(1) == "1"
    # Home Assistant raises for enum values outside the options
    assert description.value_fn(5) is None
