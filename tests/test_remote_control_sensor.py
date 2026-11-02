from custom_components.solakon_one.remote_control import RemoteControlMode
from custom_components.solakon_one.sensor import SENSOR_ENTITY_DESCRIPTIONS


def test_remote_control_sensor_normalizes_disabled_register_values() -> None:
    description = next(
        description
        for description in SENSOR_ENTITY_DESCRIPTIONS
        if description.key == "remote_control"
    )

    assert description.value_fn is not None
    assert description.value_fn(8) is RemoteControlMode.DISABLED
    assert description.value_fn(9) is RemoteControlMode.GRID_DISCHARGE
