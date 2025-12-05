"""Constants for the Solakon ONE integration."""
from typing import Final

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

DOMAIN: Final = "solakon_one"
DEFAULT_NAME: Final = "Solakon ONE"
DEFAULT_PORT: Final = 502
DEFAULT_SLAVE_ID: Final = 1
DEFAULT_SCAN_INTERVAL: Final = 30
SCAN_INTERVAL: Final = 30

UOM_MAPPING = {
    "kW": UnitOfPower.KILO_WATT,
    "W": UnitOfPower.WATT,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
    "V": UnitOfElectricPotential.VOLT,
    "A": UnitOfElectricCurrent.AMPERE,
    "Hz": UnitOfFrequency.HERTZ,
    "°C": UnitOfTemperature.CELSIUS,
    "%": PERCENTAGE,
    "kvar": "kvar",
    "var": "var",
    "s": UnitOfTime.SECONDS,
}


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

    # Protocol & Device Info (Table 3-5)
    "protocol_version": {"address": 39000, "count": 2, "type": "u32"},
    "rated_power": {"address": 39053, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "max_active_power": {"address": 39055, "count": 2, "type": "i32", "scale": 1, "unit": "W"},

    # Status
    "status_1": {"address": 39063, "count": 1, "type": "bitfield16"},
    "alarm_1": {"address": 39067, "count": 1, "type": "bitfield16"},
    "alarm_2": {"address": 39068, "count": 1, "type": "bitfield16"},
    "alarm_3": {"address": 39069, "count": 1, "type": "bitfield16"},
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

    # EPS Information
    "eps_voltage": {"address": 31010, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "eps_current": {"address": 31011, "count": 1, "type": "i16", "scale": 10, "unit": "A"},
    "eps_power": {"address": 31047, "count": 2, "type": "i32", "scale": 1, "unit": "W"},

    # Grid Information
    "grid_r_voltage": {"address": 39123, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "grid_s_voltage": {"address": 39124, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "grid_t_voltage": {"address": 39125, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "inverter_r_current": {"address": 39126, "count": 2, "type": "i32", "scale": 1000, "unit": "A"},
    "inverter_s_current": {"address": 39128, "count": 2, "type": "i32", "scale": 1000, "unit": "A"},
    "inverter_t_current": {"address": 39130, "count": 2, "type": "i32", "scale": 1000, "unit": "A"},
    "active_power": {"address": 39134, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "reactive_power": {"address": 39136, "count": 2, "type": "i32", "scale": 1000, "unit": "kvar"},
    "power_factor": {"address": 39138, "count": 1, "type": "i16", "scale": 1000},
    "grid_frequency": {"address": 39139, "count": 1, "type": "i16", "scale": 100, "unit": "Hz"},

    # Temperature
    "internal_temp": {"address": 39141, "count": 1, "type": "i16", "scale": 10, "unit": "°C"},

    # Energy Statistics
    "cumulative_generation": {"address": 39149, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},
    "daily_generation": {"address": 39151, "count": 2, "type": "u32", "scale": 100, "unit": "kWh"},

    # Battery Information
    "battery1_voltage": {"address": 39227, "count": 1, "type": "i16", "scale": 10, "unit": "V"},
    "battery1_current": {"address": 39228, "count": 2, "type": "i32", "scale": 1000, "unit": "A"},
    "battery1_power": {"address": 39230, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "battery_combined_power": {"address": 39237, "count": 2, "type": "i32", "scale": 1, "unit": "W"},
    "battery_soc": {"address": 39424, "count": 1, "type": "i16", "scale": 1, "unit": "%"},
    "battery_max_charge_current": {"address": 46607, "count": 1, "type": 'i16', "scale": 10, "unit": 'A', "rw": True},
    "battery_max_discharge_current": {"address": 46608, "count": 1, "type": 'i16', "scale": 10, "unit": 'A', "rw": True},

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
    # "work_mode": {"address": 49203, "count": 1, "type": "u16", "scale": 1, "rw": True},
    "network_status": {"address": 49240, "count": 1, "type": "u16", "scale": 1},
}

# Sensor definitions for Home Assistant
SENSOR_DEFINITIONS = {
    # Power sensors
    "pv1_power": {
        "name": "PV1 Power",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
    },
    "pv2_power": {
        "name": "PV2 Power",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
    },
    "pv3_power": {
        "name": "PV3 Power",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
    },
    "pv4_power": {
        "name": "PV4 Power",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
    },
    "total_pv_power": {
        "name": "PV Power",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
    },
    "active_power": {
        "name": "Active Power",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
    },
    "reactive_power": {
        "name": "Reactive Power",
        "device_class": "reactive_power",
        "state_class": "measurement",
        "unit": "kvar",
    },
    "battery_combined_power": {
        "name": "Battery Power",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
    },
    "battery_soc": {
        "name": "Battery State of Charge",
        "device_class": "battery",
        "state_class": "measurement",
        "unit": "%",
    },
    "eps_power": {
        "name": "EPS Power",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
        "icon": "mdi:solar-power",
    },

    # Voltage sensors
    "pv1_voltage": {
        "name": "PV1 Voltage",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit": "V",
    },
    "pv2_voltage": {
        "name": "PV2 Voltage",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit": "V",
    },
    "pv3_voltage": {
        "name": "PV3 Voltage",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit": "V",
    },
    "pv4_voltage": {
        "name": "PV4 Voltage",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit": "V",
    },
    "grid_r_voltage": {
        "name": "Grid R Voltage",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit": "V",
    },
    "battery1_voltage": {
        "name": "Battery Voltage",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit": "V",
    },
    "eps_voltage": {
        "name": "EPS Voltage",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit": "V",
        "icon": "mdi:flash",
    },

    # Current sensors
    "pv1_current": {
        "name": "PV1 Current",
        "device_class": "current",
        "state_class": "measurement",
        "unit": "A",
    },
    "pv2_current": {
        "name": "PV2 Current",
        "device_class": "current",
        "state_class": "measurement",
        "unit": "A",
    },
    "pv3_current": {
        "name": "PV3 Current",
        "device_class": "current",
        "state_class": "measurement",
        "unit": "A",
    },
    "pv4_current": {
        "name": "PV4 Current",
        "device_class": "current",
        "state_class": "measurement",
        "unit": "A",
    },
    "battery1_current": {
        "name": "Battery Current",
        "device_class": "current",
        "state_class": "measurement",
        "unit": "A",
    },
    "eps_current": {
        "name": "EPS Current",
        "device_class": "current",
        "state_class": "measurement",
        "unit": "A",
        "icon": "mdi:current-dc",
    },

    # Energy sensors
    "cumulative_generation": {
        "name": "Total Energy",
        "device_class": "energy",
        "state_class": "total_increasing",
        "unit": "kWh",
    },
    "daily_generation": {
        "name": "Daily Energy",
        "device_class": "energy",
        "state_class": "total_increasing",
        "unit": "kWh",
    },

    # Temperature sensors
    "internal_temp": {
        "name": "Internal Temperature",
        "device_class": "temperature",
        "state_class": "measurement",
        "unit": "°C",
    },

    # Other sensors
    "power_factor": {
        "name": "Power Factor",
        "device_class": "power_factor",
        "state_class": "measurement",
    },
    "grid_frequency": {
        "name": "Grid Frequency",
        "device_class": "frequency",
        "state_class": "measurement",
        "unit": "Hz",
    },
    "grid_standard_code": {
       "name": "Grid Standard Code",
        "device_class": "sensor",
    },

    # Control Status Sensors (showing current values of controllable parameters)
    "eps_output": {
        "name": "EPS Output Mode",
    },
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
    "minimum_soc": {
        "name": "Minimum State of Charge",
        "device_class": "battery",
        "state_class": "measurement",
        "unit": "%",
    },
    "maximum_soc": {
        "name": "Maximum State of Charge",
        "device_class": "battery",
        "state_class": "measurement",
        "unit": "%",
    },
    "minimum_soc_ongrid": {
        "name": "Minimum SoC OnGrid",
        "device_class": "battery",
        "state_class": "measurement",
        "unit": "%",
    },
    "battery_max_charge_current": {
        "name": "Maximum Charge Current",
        "device_class": "current",
        "state_class": "number",
        "unit": "A",
    },
    "battery_max_discharge_current":{
        "name": "Maximum Discharge Current",
        "device_class": "current",
        "state_class": "number",
        "unit": "A",
    },
    # "work_mode": {
    #     "name": "Work Mode",
    #     "icon": "mdi:cog",
    # },
    "network_status": {
        "name": "Network Status",
        "category": "diagnostic",
    },

    # Remote Control Status Sensors
    "remote_control": {
        "name": "Remote Control Status",
    },
    "remote_timeout_set": {
        "name": "Remote Timeout Setting",
        "device_class": "duration",
        "state_class": "measurement",
        "unit": "s",
    },
    "remote_active_power": {
        "name": "Remote Active Power Command",
        "device_class": "power",
        "state_class": "measurement",
        "unit": "W",
    },
    "remote_reactive_power": {
        "name": "Remote Reactive Power Command",
        "device_class": "reactive_power",
        "state_class": "measurement",
        "unit": "var",
    },
    "remote_timeout_countdown": {
        "name": "Remote Timeout Countdown",
        "device_class": "duration",
        "state_class": "measurement",
        "unit": "s",
    },
}

# Select entity definitions for Home Assistant
SELECT_DEFINITIONS = {
    "eps_output": {
        "name": "EPS Output Control",
        "options": {
            0: "Disable",
            2: "EPS Mode",
            3: "UPS Mode",
        },
    },
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
    "remote_control_mode": {
        "name": "Remote Control Mode",
        "options": {
            0: "Disabled",
            1: "INV Discharge (PV Priority)",
            3: "INV Charge (PV Priority)",
            5: "Battery Discharge",
            7: "Battery Charge",
            9: "Grid Discharge",
            11: "Grid Charge",
            13: "INV Discharge (AC First)",
            15: "INV Charge (AC First)",
        },
    },
    "force_mode": {
        "name": "Force Mode",
        "options": {
            0: "Disabled",
            1: "Force Discharge",
            3: "Force Charge",
        },
    },
}

# Number entity definitions for Home Assistant
NUMBER_DEFINITIONS = {
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
    "minimum_soc": {
        "name": "Minimum SoC Control",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": "%",
        "mode": "slider",
        "category": "config",
    },
    "maximum_soc": {
        "name": "Maximum SoC Control",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": "%",
        "mode": "slider",
        "category": "config",
    },
    "minimum_soc_ongrid": {
        "name": "Minimum SoC OnGrid Control",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": "%",
        "mode": "slider",
        "category": "config",
    },
    "battery_max_charge_current": {
        "name": "Maximum Charge Current",
        "min": 0,
        "max": 40,
        "step": 1,
        "unit": "A",
        "mode": "box",
        "category": "config",
    },
    "battery_max_discharge_current":{
        "name": "Maximum Discharge Current",
        "min": 0,
        "max": 40,
        "step": 1,
        "unit": "A",
        "mode": "box",
        "category": "config",
    },
    "remote_active_power": {
        "name": "Remote Active Power Control",
        "min": -100000,  # -100kW (charging/import)
        "max": 100000,   # +100kW (discharging/export)
        "step": 100,
        "unit": "W",
        "device_class": "power",
        "mode": "box",
    },
    "remote_reactive_power": {
        "name": "Remote Reactive Power Control",
        "min": -100000,
        "max": 100000,
        "step": 100,
        "unit": "var",
        "mode": "box",
    },
    "remote_timeout_set": {
        "name": "Remote Timeout Control",
        "min": 0,
        "max": 3600,  # 1 hour max
        "step": 10,
        "unit": "s",
        "mode": "box",
    },
    "force_duration": {
        "name": "Force Mode Duration",
        "min": 0,
        "max": 1092,  # 65535 seconds = ~1092 minutes
        "step": 1,
        "unit": "min",
        "mode": "slider",
    },
    "force_power": {
        "name": "Force Mode Power",
        "min": 0,
        "max": 1200,  # Will be validated based on mode (1200W charge, 800W discharge)
        "step": 10,
        "unit": "W",
        "device_class": "power",
        "mode": "box",
    },
}
