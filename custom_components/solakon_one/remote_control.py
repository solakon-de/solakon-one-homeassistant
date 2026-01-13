"""Remote Control helper for Solakon ONE integration.

Based on Remote Control Definition V1.5
"""

from enum import IntEnum


class RemoteControlTarget(IntEnum):
    """Remote control target types (bits 3:2 of register 46001)."""

    AC = 0b00  # AC port
    BATTERY = 0b01  # Battery port
    GRID = 0b10  # Grid/Meter port
    AC_GRID_FIRST = 0b11  # AC port with grid power used first


class RemoteControlDirection(IntEnum):
    """Remote control direction (bit 1 of register 46001)."""

    GENERATION = 0  # Power generation system (discharge/export)
    CONSUMPTION = 1  # Power consumption system (charge/import)


class RemoteControlMode(IntEnum):
    """Remote control modes combining target and direction."""

    DISABLED = 0
    INV_DISCHARGE_PV_PRIORITY = (
        1  # Target: AC(00), Direction: Generation(0), Enabled(1) = 0b0001
    )
    INV_CHARGE_PV_PRIORITY = (
        3  # Target: AC(00), Direction: Consumption(1), Enabled(1) = 0b0011
    )
    BATTERY_DISCHARGE = (
        5  # Target: Battery(01), Direction: Generation(0), Enabled(1) = 0b0101
    )
    BATTERY_CHARGE = (
        7  # Target: Battery(01), Direction: Consumption(1), Enabled(1) = 0b0111
    )
    GRID_DISCHARGE = (
        9  # Target: Grid(10), Direction: Generation(0), Enabled(1) = 0b1001
    )
    GRID_CHARGE = 11  # Target: Grid(10), Direction: Consumption(1), Enabled(1) = 0b1011
    INV_DISCHARGE_AC_FIRST = (
        13  # Target: AC Grid First(11), Direction: Generation(0), Enabled(1) = 0b1101
    )
    INV_CHARGE_AC_FIRST = (
        15  # Target: AC Grid First(11), Direction: Consumption(1), Enabled(1) = 0b1111
    )


def encode_remote_control(
    enabled: bool,
    direction: RemoteControlDirection,
    target: RemoteControlTarget,
) -> int:
    """Encode remote control register value from components.

    Register 46001 bit structure:
    - Bit 0: Remote control enable (0=Disable, 1=Enable)
    - Bit 1: Direction (0=power-generation, 1=power-consumption)
    - Bits 3:2: Controlled target (00=AC, 01=Battery, 10=Grid, 11=AC grid first)
    - Bits 15:4: Reserved (should be 0)

    Args:
        enabled: Whether remote control is enabled
        direction: Power direction (generation or consumption)
        target: Control target (AC, Battery, Grid, or AC with grid first)

    Returns:
        16-bit register value
    """
    value = 0
    if enabled:
        value |= 0b0001  # Bit 0: Enable
    if direction == RemoteControlDirection.CONSUMPTION:
        value |= 0b0010  # Bit 1: Direction
    value |= (target & 0b11) << 2  # Bits 3:2: Target
    return value


def decode_remote_control(
    value: int,
) -> tuple[bool, RemoteControlDirection, RemoteControlTarget]:
    """Decode remote control register value into components.

    Args:
        value: 16-bit register value

    Returns:
        Tuple of (enabled, direction, target)
    """
    enabled = bool(value & 0b0001)
    direction = RemoteControlDirection((value >> 1) & 0b0001)
    target = RemoteControlTarget((value >> 2) & 0b0011)
    return enabled, direction, target


def mode_to_register_value(mode: RemoteControlMode) -> int:
    """Convert a RemoteControlMode to register value.

    Args:
        mode: The remote control mode

    Returns:
        16-bit register value for register 46001
    """
    if mode == RemoteControlMode.DISABLED:
        return 0

    # Extract components from mode value
    # Mode values are structured as: (target << 2) | (direction << 1) | enabled
    enabled = True
    direction = RemoteControlDirection((mode >> 1) & 0b0001)
    target = RemoteControlTarget((mode >> 2) & 0b0011)

    return encode_remote_control(enabled, direction, target)


def register_value_to_mode(value: int) -> RemoteControlMode:
    """Convert a register value to RemoteControlMode.

    Args:
        value: 16-bit register value from register 46001

    Returns:
        The corresponding RemoteControlMode
    """
    if value == 0 or not (value & 0b0001):
        return RemoteControlMode.DISABLED

    # Mode value matches lower 4 bits of register when enabled
    mode_value = value & 0b1111

    try:
        return RemoteControlMode(mode_value)
    except ValueError:
        # Invalid mode, return disabled
        return RemoteControlMode.DISABLED


def get_mode_description(mode: RemoteControlMode) -> str:
    """Get a human-readable description of the mode.

    Args:
        mode: The remote control mode

    Returns:
        Description string
    """
    descriptions = {
        RemoteControlMode.DISABLED: "Disabled",
        RemoteControlMode.INV_DISCHARGE_PV_PRIORITY: "INV Discharge (PV Priority)",
        RemoteControlMode.INV_CHARGE_PV_PRIORITY: "INV Charge (PV Priority)",
        RemoteControlMode.BATTERY_DISCHARGE: "Battery Discharge",
        RemoteControlMode.BATTERY_CHARGE: "Battery Charge",
        RemoteControlMode.GRID_DISCHARGE: "Grid Discharge",
        RemoteControlMode.GRID_CHARGE: "Grid Charge",
        RemoteControlMode.INV_DISCHARGE_AC_FIRST: "INV Discharge (AC First)",
        RemoteControlMode.INV_CHARGE_AC_FIRST: "INV Charge (AC First)",
    }
    return descriptions.get(mode, "Unknown")
