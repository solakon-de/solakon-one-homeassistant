# Solakon ONE Home Assistant Integration

A complete Home Assistant custom integration for Solakon ONE devices using Modbus TCP communication.

> ⚠️ **IMPORTANT**: This is a Home Assistant **Integration**, not an Add-on.
> - Do NOT add this as an Add-on repository
> - Install it through HACS as an Integration (see instructions below)

## Changelog

### Latest Version
**New Features:**
- ✨ **Device Control Entities**: Control your Solakon ONE device directly from Home Assistant
  - EPS Output Mode control (Disable/EPS/UPS)
  - Remote Control Mode with 9 operating modes
  - Battery SoC limits (Minimum/Maximum/OnGrid)
  - Remote Active/Reactive Power control
  - Remote timeout settings
- 📊 **New Sensors**: Added control status sensors to monitor current device settings
  - EPS Output Mode status
  - Battery SoC limit settings
  - Remote control status and commands
  - Network status
- 🔧 **Improved Energy Dashboard Integration**: Comprehensive documentation for battery integration workaround
- 📖 **Documentation Updates**: Accurate Energy Dashboard integration guide with step-by-step battery setup

**Bug Fixes:**
- Fixed misleading documentation about Grid Import/Export sensors (not currently supported)
- Corrected Energy Dashboard integration instructions

### Previous Versions
- Initial release with basic monitoring capabilities

## Features

### Monitoring
- Real-time monitoring of all inverter parameters
- PV string monitoring (voltage, current, power)
- Battery management (SOC, power, voltage, current, temperature)
- Energy statistics (total and daily generation)
- Temperature monitoring
- Alarm and status monitoring
- Power factor and grid frequency monitoring

### Device Control
- **EPS Output Control**: Switch between Disable, EPS Mode, and UPS Mode
- **Remote Control Mode**: 9 different operating modes including:
  - INV Discharge/Charge (PV Priority or AC First)
  - Battery Discharge/Charge
  - Grid Discharge/Charge
- **Battery SoC Management**: Set minimum and maximum state of charge limits
- **Remote Power Control**: Set active and reactive power commands
- **Timeout Management**: Configure remote control timeout settings

### Integration
- Full UI configuration support
- Configurable update intervals
- Energy Dashboard compatible (solar production works out-of-the-box)
- Battery integration via helper sensors

## Monitored Sensors

### Power Sensors
- PV Power (total from all strings)
- Active Power
- Reactive Power
- Load Power
- Battery Power

### Voltage & Current
- PV1/PV2/PV3/PV4 Voltage & Current
- Grid Phase Voltages (R/S/T)
- Battery Voltage & Current
- Load Voltage & Current

### Energy Statistics
- Total Energy Generated
- Daily Energy Generation

### Battery Information
- Battery Power
- Battery Voltage
- Battery Current
- Battery State of Charge (SOC)

### System Information
- Internal Temperature
- Power Factor
- Grid Frequency
- Network Status

### Control Status Sensors
These sensors display the current values of controllable parameters:
- EPS Output Mode (current mode: Disable/EPS/UPS)
- Minimum/Maximum/OnGrid SoC Settings
- Remote Control Status
- Remote Active/Reactive Power Commands
- Remote Timeout Settings

## Installation

### Prerequisites
- Home Assistant 2024.1.0 or newer
- HACS (Home Assistant Community Store) installed
- Your Solakon ONE device connected to your network with Modbus TCP enabled

### HACS Installation (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on **"Integrations"** (NOT Add-ons!)
3. Click the **three dots menu** in the top right → **"Custom repositories"**
4. Add this repository URL: `https://github.com/solakon-de/solakon-one-homeassistant`
5. Select category: **"Integration"** (⚠️ NOT "Add-on"!)
6. Click **"Add"**
7. Close the custom repositories dialog
8. Click **"+ Explore & Download Repositories"**
9. Search for **"Solakon ONE"** and install it
10. **Restart Home Assistant**
11. Go to **Settings → Devices & Services**
12. Click **"+ Add Integration"**
13. Search for **"Solakon ONE"** and configure it

### Manual Installation

1. Copy the `custom_components/solakon_one` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services

## Configuration

### Via UI (Recommended)

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Solakon ONE"
4. Enter configuration:
   - **Host**: IP address of your Solakon ONE device
   - **Port**: Modbus TCP port (default: 502)
   - **Device Name**: Friendly name for your device
   - **Modbus Device ID**: Usually 1 (range: 1-247)
   - **Update Interval**: How often to poll (1-300 seconds)

### Network Requirements

- Ensure your Solakon ONE device is connected to your network
- Modbus TCP must be enabled on the device
- Default Modbus TCP port is 502
- Device must be accessible from Home Assistant

## Device Control

The integration provides control entities to manage your Solakon ONE device directly from Home Assistant.

### Select Entities

**EPS Output Control**
- Switch between operating modes:
  - `Disable`: EPS output disabled
  - `EPS Mode`: Emergency Power Supply mode
  - `UPS Mode`: Uninterruptible Power Supply mode

**Remote Control Mode**
- Control device operation with 9 modes:
  - `Disabled`: Remote control off
  - `INV Discharge (PV Priority)`: Inverter discharge with PV priority
  - `INV Charge (PV Priority)`: Inverter charge with PV priority
  - `Battery Discharge`: Direct battery discharge
  - `Battery Charge`: Direct battery charge
  - `Grid Discharge`: Grid-powered discharge
  - `Grid Charge`: Grid-powered charge
  - `INV Discharge (AC First)`: Inverter discharge with AC priority
  - `INV Charge (AC First)`: Inverter charge with AC priority

### Number Entities

**Battery SoC Management**
- `Minimum SoC Control`: Set minimum battery state of charge (0-100%)
- `Maximum SoC Control`: Set maximum battery state of charge (0-100%)
- `Minimum SoC OnGrid Control`: Set minimum SoC when grid-connected (0-100%)

**Remote Power Control**
- `Remote Active Power Control`: Set active power command (-100kW to +100kW)
  - Negative values = charging/import
  - Positive values = discharging/export
- `Remote Reactive Power Control`: Set reactive power command (-100kVAR to +100kVAR)
- `Remote Timeout Control`: Set timeout for remote control commands (0-3600 seconds)

> ⚠️ **Warning**: Modifying these settings can affect your system's operation. Make sure you understand what each setting does before changing it. Some settings may require the device to be in specific modes to take effect.

## Troubleshooting

### Connection Issues

1. Verify network connectivity:
   ```bash
   ping <device-ip>
   ```

2. Test Modbus connection:
   ```bash
   telnet <device-ip> 502
   ```

3. Check Home Assistant logs:
   ```
   Settings → System → Logs → Search for "solakon"
   ```

### Common Issues

- **Cannot connect**: Verify IP address and port are correct
- **No data**: Check Modbus device ID (usually 1)
- **Intermittent data**: Increase update interval if network is slow
- **Missing sensors**: Some sensors only appear if hardware is present (e.g., battery sensors)

## Energy Dashboard Integration

### Solar Production (Works Out-of-the-Box)

To add solar production to your Energy Dashboard:

1. Go to Settings → Dashboards → Energy
2. Under **Solar production**, select "Solakon ONE Daily Energy"

### Battery Integration (Requires Setup)

The battery sensors need to be configured as helpers before they can be used in the Energy Dashboard. Follow these steps:

#### 1. Create Template Sensors for Battery Power Split

Go to Settings → Devices & Services → Helpers → Create Helper → Template → Template a sensor

Create two template sensors with the following settings:

**Battery Discharge Power:**
- Name: `Battery Discharge Power`
- State template: `{{ max(0, 0 - states('sensor.solakon_one_battery_combined_power') | float(default=0)) }}`
- Unit of measurement: `W`
- Device class: `Power`
- State class: `Measurement`

**Battery Charge Power:**
- Name: `Battery Charge Power`
- State template: `{{ max(0, states('sensor.solakon_one_battery_combined_power') | float(default=0)) }}`
- Unit of measurement: `W`
- Device class: `Power`
- State class: `Measurement`

#### 2. Create Riemann Sum Integral Sensors

Go to Settings → Devices & Services → Helpers → Create Helper → Integration - Riemann sum integral sensor

Create two integral sensors:

**Battery Discharge Energy:**
- Input sensor: `Battery Discharge Power` (from step 1)
- Name: `Battery Discharge Energy`
- Integration method: `Left Riemann sum`
- Precision: `2`
- Metric prefix: `k` (kilo)

**Battery Charge Energy:**
- Input sensor: `Battery Charge Power` (from step 1)
- Name: `Battery Charge Energy`
- Integration method: `Left Riemann sum`
- Precision: `2`
- Metric prefix: `k` (kilo)

#### 3. Add to Energy Dashboard

1. Go to Settings → Dashboards → Energy
2. Under **Battery systems**, click "Add battery system"
3. Configure:
   - **Energy going in to the battery**: Select "Battery Charge Energy"
   - **Energy going out of the battery**: Select "Battery Discharge Energy"

### Grid Import/Export (Not Currently Supported)

Grid import and export sensors are not currently available in this integration. These values would need to be derived from the available power sensors or added in a future update if the Modbus registers support them.

## Automation Examples

### Battery Power Monitoring
```yaml
automation:
  - alias: "Battery Discharging Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solakon_one_battery_combined_power
        below: -5000  # Alert when discharging more than 5kW
    action:
      - service: notify.mobile_app
        data:
          message: "Battery is discharging at high rate!"
```

### Control Battery SoC Based on Time
```yaml
automation:
  - alias: "Set Battery Limits for Night"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: number.set_value
        target:
          entity_id: number.solakon_one_minimum_soc_control
        data:
          value: 20
      - service: number.set_value
        target:
          entity_id: number.solakon_one_maximum_soc_control
        data:
          value: 100
```

### Switch to EPS Mode on Grid Failure
```yaml
automation:
  - alias: "Enable EPS Mode on Grid Loss"
    trigger:
      - platform: state
        entity_id: sensor.solakon_one_network_status
        to: "0"  # Adjust based on your grid status values
    action:
      - service: select.select_option
        target:
          entity_id: select.solakon_one_eps_output_control
        data:
          option: "EPS Mode"
```

## Device Control via Entities

Device control is implemented using Home Assistant entities (Select and Number entities). Use these entities in your dashboards and automations:

**Available Control Entities:**
- `select.solakon_one_eps_output_control`: EPS/UPS mode selection
- `select.solakon_one_remote_control_mode`: Remote control mode selection
- `number.solakon_one_minimum_soc_control`: Minimum battery SoC
- `number.solakon_one_maximum_soc_control`: Maximum battery SoC
- `number.solakon_one_minimum_soc_ongrid_control`: Minimum SoC when grid-connected
- `number.solakon_one_remote_active_power_control`: Active power command
- `number.solakon_one_remote_reactive_power_control`: Reactive power command
- `number.solakon_one_remote_timeout_control`: Remote control timeout

**Future Services (Planned):**
- `solakon_one.refresh_data`: Manually refresh all sensor data
- `solakon_one.set_time_of_use`: Configure TOU schedules

## Support

For issues or questions:
- Report issues on [GitHub](https://github.com/solakon-de/solakon-one-homeassistant/issues)

## License

This integration is provided as-is under the MIT License.