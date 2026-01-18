"""Constants for the Solakon ONE integration."""

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "solakon_one"

CONF_DEVICE_ID: Final = "slave_id"

DEFAULT_MANUFACTURER: Final = "Solakon"
DEFAULT_MODEL: Final = "ONE"
DEFAULT_NAME: Final = "Solakon ONE"
DEFAULT_PORT: Final = 502
DEFAULT_DEVICE_ID: Final = 1
DEFAULT_SCAN_INTERVAL: Final = 30

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
]

# fmt: off
# Register definitions
REGISTERS = {
    # Model Information (Table 3-1)
    "model_name": {"address": 30000, "count": 16, "type": "string"},
    "serial_number": {"address": 30016, "count": 16, "type": "string"},
    "mfg_id": {"address": 30032, "count": 16, "type": "string"},

    # Version Information (Table 3-2)
    "master_version": {"address": 36001, "count": 1, "type": "u16"},
    "slave_version": {"address": 36002, "count": 1, "type": "u16"},
    "manager_version": {"address": 36003, "count": 1, "type": "u16"},

    # Battery Version Information (Table 3-3)
    "bms1_design_energy": {"address": 37635, "count": 1, "type": "i16", "scale": 0.1, "unit": "Wh"},

    "bms1_soh": {"address": 37624, "count": 1, "type": "u16", "scale": 1, "unit": "%"},
    "bms2_soh": {"address": 38322, "count": 1, "type": "u16", "scale": 1, "unit": "%"},
    "bms1_soc": {"address": 37612, "count": 1, "type": "i16", "scale": 1, "unit": "%"},
    "bms2_soc": {"address": 38310, "count": 1, "type": "i16", "scale": 1, "unit": "%"},

    # Protocol & Device Info (Table 3-5)
    "protocol_version": {"address": 39000, "count": 2, "type": "u32"},
    "rated_power": {"address": 39053, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "max_active_power": {"address": 39055, "count": 2, "type": "i32", "scale": 1, "unit": "W"},

    # Status
    "status_1": {"address": 39063, "count": 1, "type": "u16"}, # bitfield16
    "status_3": {"address": 39065, "count": 2, "type": "u32"}, # bitfield32
    "grid_status": {"address": 39065, "count": 2, "type": "bitfield32", "bit": 0}, # true=off-grid, false=grid connected
    "alarm_1": {"address": 39067, "count": 1, "type": "u16"}, #bitfield16
    "alarm_2": {"address": 39068, "count": 1, "type": "u16"}, #bitfield16
    "alarm_3": {"address": 39069, "count": 1, "type": "u16"}, #bitfield16
    "grid_standard_code": {"address": 49079, "count": 1, "type": 'u16'},

    # PV Input
    "pv1_voltage": {"address": 39070, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "pv1_current": {"address": 39071, "count": 1, "type": "i16", "scale": 100, "unit": "A"},
    "pv1_power": {"address": 39279, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "pv2_voltage": {"address": 39072, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "pv2_current": {"address": 39073, "count": 1, "type": "i16", "scale": 100, "unit": "A"},
    "pv2_power": {"address": 39281, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "pv3_voltage": {"address": 39074, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "pv3_current": {"address": 39075, "count": 1, "type": "i16", "scale": 100, "unit": "A"},
    "pv3_power": {"address": 39283, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "pv4_voltage": {"address": 39076, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "pv4_current": {"address": 39077, "count": 1, "type": "i16", "scale": 100, "unit": "A"},
    "pv4_power": {"address": 39285, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "total_pv_power": {"address": 39118, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "pv_total_energy": {"address": 39601, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},

    # EPS Information
    "eps_voltage": {"address": 39201, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "eps_current": {"address": 39204, "count": 1, "type": "i16", "scale": 10, "unit": "A"},
    "eps_power": {"address": 39216, "count": 2, "type": "i32", "scale": 1, "unit": "W"},

    # Grid Information
    "grid_r_voltage": {"address": 39123, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "grid_s_voltage": {"address": 39124, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "grid_t_voltage": {"address": 39125, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "grid_frequency": {"address": 39139, "count": 1, "type": "i16", "scale": 100, "unit": "Hz"},
    "active_power": {"address": 39134, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "reactive_power": {"address": 39136, "count": 2, "type": "i32", "scale": 1000, "unit": "kvar"},
    "power_factor": {"address": 39138, "count": 1, "type": "i16", "scale": 1000},
    "grid_total_export_energy": {"address": 39621, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},
    "grid_total_import_energy": {"address": 39625, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},

    # Inverter Information
    "inverter_r_current": {"address": 39126, "count": 2, "type": "i32", "scale": 1000, "unit": "A"},
    "inverter_s_current": {"address": 39128, "count": 2, "type": "i32", "scale": 1000, "unit": "A"},
    "inverter_t_current": {"address": 39130, "count": 2, "type": "i32", "scale": 1000, "unit": "A"},
    "inverter_r_frequency": {"address": 39272, "count": 1, "type": "i16", "scale": 100, "unit": "Hz"},
    "inverter_s_frequency": {"address": 39273, "count": 1, "type": "i16", "scale": 100, "unit": "Hz"},
    "inverter_t_frequency": {"address": 39274, "count": 1, "type": "i16", "scale": 100, "unit": "Hz"},

    # Temperature
    "internal_temp": {"address": 39141, "count": 1, "type": "i16", "scale": 10, "unit": "°C"},
    "bms1_ambient_temp": {"address": 37611, "count": 1, "type": "i16", "scale": 10, "unit": "°C"},
    "bms1_max_temp": {"address": 37617, "count": 1, "type": "i16", "scale": 10, "unit": "°C"},
    "bms1_min_temp": {"address": 37618, "count": 1, "type": "i16", "scale": 10, "unit": "°C"},
    "bms2_ambient_temp": {"address": 38309, "count": 1, "type": "i16", "scale": 10, "unit": "°C"},
    "bms2_max_temp": {"address": 38315, "count": 1, "type": "i16", "scale": 10, "unit": "°C"},
    "bms2_min_temp": {"address": 38316, "count": 1, "type": "i16", "scale": 10, "unit": "°C"},

    # Energy Statistics
    "cumulative_generation": {"address": 39149, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},
    "daily_generation": {"address": 39151, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},

    # Battery Information
    "battery1_voltage": {"address": 39227, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "battery1_current": {"address": 39228, "count": 2, "type": "i32", "scale": 1000, "unit": "A"},
    "battery1_power": {"address": 39230, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "battery_combined_power": {"address": 39237, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "battery_power": {"address": 39230, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "battery_soc": {"address": 39424, "count": 1, "type": "i16", "scale": 1, "unit": "%"},
    "battery_max_charge_current": {"address": 46607, "count": 1, "type": 'i16', "scale": 10, "unit": 'A', "rw": True},
    "battery_max_discharge_current": {"address": 46608, "count": 1, "type": 'i16', "scale": 10, "unit": 'A', "rw": True},
    "battery_total_charge_energy": {"address": 39605, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},
    "battery_total_discharge_energy": {"address": 39609, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},

    # Remote Control Registers (Read/Write)
    "remote_control": {"address": 46001, "count": 1, "type": "u16", "scale": 1, "rw": True},
    "remote_timeout_set": {"address": 46002, "count": 1, "type": "u16", "scale": 1, "unit": "s", "rw": True},
    "remote_active_power": {"address": 46003, "count": 2, "type": "i32", "scale": 1, "unit": "W", "rw": True},
    "remote_reactive_power": {"address": 46005, "count": 2, "type": "i32", "scale": 1, "unit": "var", "rw": True},
    "remote_timeout_countdown": {"address": 46007, "count": 1, "type": "u16", "scale": 1, "unit": "s"},

    # Control Registers (Read/Write)
    "eps_output": {"address": 46613, "count": 1, "type": "u16", "scale": 1, "rw": True},
    # "export_power_limit": {"address": 46616, "count": 2, "type": "i32", "scale": 1, "unit": "W", "rw": True},
    # "import_power_limit": {"address": 46501, "count": 2, "type": "i32", "scale": 1, "unit": "W", "rw": True},
    # "export_peak_limit": {"address": 46504, "count": 2, "type": "i32", "scale": 1, "unit": "W", "rw": True},
    "minimum_soc": {"address": 46609, "count": 1, "type": "u16", "scale": 1, "unit": "%", "rw": True},
    "maximum_soc": {"address": 46610, "count": 1, "type": "u16", "scale": 1, "unit": "%", "rw": True},
    "minimum_soc_ongrid": {"address": 46611, "count": 1, "type": "u16", "scale": 1, "unit": "%", "rw": True},
    "operating_mode": {"address": 49203, "count": 1, "type": "u16", "scale": 1, "rw": True}, # work_mode
    "network_status": {"address": 49240, "count": 1, "type": "u16", "scale": 1},
}
# fmt: on
