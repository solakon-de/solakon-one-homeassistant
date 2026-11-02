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
- ⚡ **Meter/CT Sensors**: Full Meter1/CT1 and Meter2/CT2 register blocks plus the
  aggregated grid reading, so systems with an external meter or CT can see what the
  meter measures (disabled by default, see [Meter / CT Sensors](#meter--ct-sensors))
- 🔧 **Improved Energy Dashboard Integration**: Comprehensive documentation for battery integration workaround
- 📖 **Documentation Updates**: Accurate Energy Dashboard integration guide with step-by-step battery setup

**Bug Fixes:**
- Fixed misleading documentation about Grid Import/Export sensors (they need a meter or CT — see [Grid Import/Export](#grid-importexport-requires-a-meter-or-ct))
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
- Grid metering via an external meter or CT (Meter1/CT1 and Meter2/CT2)

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
- Battery integration works directly with native energy sensors

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

All counters are seen from the Solakon ONE, not from your house:

- **PV energy**: energy produced by the solar modules connected to the ONE
- **Battery charge energy**: energy that went into the battery (from PV or from the AC side)
- **Battery discharge energy**: energy that came out of the battery
- **Grid export energy**: energy the ONE delivered on its AC side (into the house, and from there possibly into the grid)
- **Grid import energy**: energy the ONE drew from its AC side, e.g. to charge the battery from the grid
- **Total energy generated** / **Daily energy**: inverter generation counters

These are not your household's grid import and export. For those you need a meter, see
[Grid Import/Export](#grid-importexport-requires-a-meter-or-ct).

The lifetime counters never decrease: a single reading lower than the previous one (e.g.
after a Modbus timeout or a firmware update) is ignored, so it can't cause spikes in the
Energy Dashboard.

Daily counters (PV, battery charge/discharge, grid export/import today) are disabled by
default. The device resets them at its own day boundary, which may not match your Home
Assistant time zone. If you need daily values in your time zone, use a
[Utility Meter](https://www.home-assistant.io/integrations/utility_meter/) on the
lifetime counters instead.

### Battery Information
- Battery Power
- Battery Voltage
- Battery Current
- Battery State of Charge (SOC)
- Battery State of Health (SOH)
- BMS min/max temperature and min/max cell voltage: the current lowest and highest value
  across all cells, not extremes over a time window

The Solakon ONE has one BMS that covers all connected battery modules, so SoC and SoH
always describe the whole battery.

### System Information
- Internal Temperature
- Power Factor
- Grid Frequency
- Network Status
- Available Import/Export Power: the power the device can currently take in or deliver,
  after derating (e.g. by battery temperature)

### Meter / CT Sensors

These read the Meter1/CT1 (`38801`–`38846`) and Meter2/CT2 (`38901`–`38946`) register
blocks and the aggregated `[Meter collection] Active power` register (`39168`). They
only carry data when an external meter or CT is connected, so **the measurement sensors
are disabled by default** — see [Grid Import/Export](#grid-importexport-requires-a-meter-or-ct)
for how to enable them. The two connection-state entities stay enabled so you can tell
whether a meter is present at all.

- Meter Connection State (Meter 1 / Meter 2) — enabled by default, reports whether the
  inverter sees a meter
- Grid Meter Power (aggregated across meters; positive = export, negative = import)
- Per meter: Power, Reactive Power, Apparent Power, Power Factor, Frequency
- Per meter and phase (R/S/T), as diagnostics: Voltage, Current, Power, Reactive
  Power, Apparent Power, Power Factor

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

### Changing the IP Address or Port

If your Solakon ONE gets a new IP address, you do not need to delete and re-add
the integration:

1. Go to Settings → Devices & Services
2. Find the **Solakon ONE** entry, click the three dots menu → **"Reconfigure"**
3. Enter the new **Host**, **Port**, or **Modbus Device ID**
4. Submit — Home Assistant verifies the device is reachable and reloads the integration

All entities keep their entity IDs, custom names, and recorded history.

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

#### How remote control works

Each mode is one value of register `46001`, built from three parts:

| Part | Values |
|---|---|
| Enable | off / on |
| Direction | *Discharge* (generation: power flows out of the device) / *Charge* (consumption: power flows into the device) |
| Target, the point the power setpoint applies to | *INV … (PV Priority)*: the inverter's AC port, PV is used first · *Battery …*: the battery port · *Grid …*: the grid meter, needs a connected meter · *INV … (AC First)*: the AC port, with power from the AC side used first |

The power setpoint is **Remote active power** (`46003`, in W, always positive; the direction
comes from the mode). **Remote reactive power** (`46005`) is a reactive power command in var
and is not needed for charging or discharging.

**Remote timeout** (`46002`, seconds) is a safety net: the device counts it down
(**Remote timeout countdown**, `46007`) and switches remote control off when it reaches 0.
Whoever controls the device has to write the setpoint again before it runs out.

Field reports ([#309](https://github.com/solakon-de/solakon-one-homeassistant/issues/309), [#41](https://github.com/solakon-de/solakon-one-homeassistant/issues/41)) show that writing the timeout can reset the mode and the power, and
writing the mode can reset the power. Set them in this order:

1. Remote timeout
2. Remote control mode
3. Remote active power

and repeat at least the power (or the timeout) before the countdown ends. On some firmware
versions the countdown has been reported to stay constant or remote control to switch itself
off early ([#41](https://github.com/solakon-de/solakon-one-homeassistant/issues/41), [#270](https://github.com/solakon-de/solakon-one-homeassistant/issues/270)); this happens on the device, not in the integration.

Energy plans and modes set in the Solakon app (e.g. *Smart meter mode*, *Überschussladen*)
are not visible over Modbus. Settings changed here are applied on the device but are not
shown in the Solakon app or web portal.

### Number Entities

**Battery SoC Management**
- `Minimum SoC Control`: Set minimum battery state of charge (0-100%)
- `Maximum SoC Control`: Set maximum battery state of charge (0-100%)
- `Minimum SoC OnGrid Control`: Set minimum SoC when grid-connected (0-100%)

**Remote Power Control**
- `Remote Active Power Control`: Set active power command (-100000W to +800W)
  - Negative values = charging/import
  - Positive values = discharging/export
- `Remote Reactive Power Control`: Set reactive power command (-100kVAR to +100kVAR, -800 to +800 while a discharge mode is active)
- `Remote Timeout Control`: Set timeout for remote control commands (0-3600 seconds)
- `Force mode power`: Power for force charge (up to 1200W) or force discharge (up to 800W)
- `Grid export power limit`: Maximum power that is exported to the grid (0-800W)

> ⚠️ **Discharge limit**: The integration does not accept discharge settings above 800W. Values above 800W are rejected for the grid export power limit, for force mode power while discharging and for the remote power setpoints while a discharge mode is active. When a discharge mode is selected, the device is read first and remote power setpoints above 800W that are left over from charging are lowered to 800W before the mode is enabled. Charging up to 1200W is not affected. Values that are already stored on the device, or that are changed outside of Home Assistant (e.g. in the Solakon app), are not corrected.

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

- **Cannot connect**: Verify IP address and port are correct — if the device's IP changed, use *Reconfigure* (see [Changing the IP Address or Port](#changing-the-ip-address-or-port))
- **No data**: Check Modbus device ID (usually 1)
- **Intermittent data**: Increase update interval if network is slow
- **Missing sensors**: Some sensors only appear if hardware is present (e.g., battery sensors)

## Energy Dashboard Integration

### Solar Production (Works Out-of-the-Box)

To add solar production to your Energy Dashboard:

1. Go to Settings → Dashboards → Energy
2. Under **Solar production**, select "PV Energy" and "PV Power"

### Battery Integration (Works Directly)

The integration provides native `Battery charge energy` and `Battery discharge energy` sensors, so no helpers are needed for the Energy Dashboard:

1. Go to Settings → Dashboards → Energy
2. Under **Battery systems**, click "Add battery system".
3. Configure:
   - **Energy going in to the battery**: Select the `Battery charge energy` sensor.
   - **Energy going out of the battery**: Select the `Battery discharge energy` sensor.

#### Optional: Real Time Power Display

If you also want live power values on the battery card, create two template power sensors first.

Go to Settings → Devices & Services → Helpers → Create Helper → Template → Template a sensor

Create two template sensors with the following settings:

**Battery Discharge Power:**
- Name: `Battery Discharge Power`
- State template: `{{ max(0, states('sensor.solakon_one_battery_power') | float(default=0)) }}`
- Unit of measurement: `W`
- Device class: `Power`
- State class: `Measurement`

**Battery Charge Power:**
- Name: `Battery Charge Power`
- State template: `{{ max(0, 0 - states('sensor.solakon_one_battery_power') | float(default=0)) }}`
- Unit of measurement: `W`
- Device class: `Power`
- State class: `Measurement`

#### Assign the Power Sensors

Back on the battery system card, you can assign the template sensors created above for real time information:
   - **Power going in to the battery**: Select the `Battery Charge Power` template sensor.
   - **Power going out of the battery**: Select the `Battery Discharge Power` template sensor.

### Grid Import/Export (Requires a Meter or CT)

The Modbus protocol does expose grid-side metering, but only through an external meter
or CT: the Meter1/CT1 block (`38801`–`38846`), the Meter2/CT2 block (`38901`–`38946`),
and the aggregated `[Meter collection] Active power` register (`39168`). The
integration reads all of them, but the meter sensors are **disabled by default**
because the registers stay at zero on systems without a meter.

#### Enable the Meter Sensors

1. Check the `Meter 1` (or `Meter 2`) diagnostic entity on the device page. It reports
   the meter's connection state — if it stays `Disconnected`, the inverter does not see
   a meter and the remaining sensors will not produce useful values.
2. On the device page, open **+N entities not shown** and enable the meter sensors you
   want. `Grid meter power` is the aggregated reading:
   **positive = exporting to the grid, negative = importing from the grid**.

#### Add Grid Import/Export to the Energy Dashboard

The Energy Dashboard needs energy (kWh), while the meter registers report power (W), so
the signed power sensor has to be split and integrated. This mirrors the battery
workaround above.

Go to Settings → Devices & Services → Helpers → Create Helper → Template → Template a sensor
and create:

**Grid Import Power:**
- Name: `Grid Import Power`
- State template: `{{ max(0, 0 - states('sensor.solakon_one_grid_meter_power') | float(default=0)) }}`
- Unit of measurement: `W`
- Device class: `Power`
- State class: `Measurement`

**Grid Export Power:**
- Name: `Grid Export Power`
- State template: `{{ max(0, states('sensor.solakon_one_grid_meter_power') | float(default=0)) }}`
- Unit of measurement: `W`
- Device class: `Power`
- State class: `Measurement`

Then create an **Integral sensor** helper for each of the two (Create Helper → Integral
sensor), with metric prefix `k` and time unit `h` to get kWh. Finally, in
Settings → Dashboards → Energy, use the resulting kWh sensors under **Grid consumption**
(import) and **Return to grid** (export).

> **Note**: These sensors have not been verified against hardware with a meter attached.
> If the sign convention or scaling looks wrong on your system, please
> [open an issue](https://github.com/solakon-de/solakon-one-homeassistant/issues).

### Solakon PowerTracker IR Integration

You can integrate the Solakon PowerTracker IR via Home Assistant's REST sensor. Add the following to your `configuration.yaml`:

```yaml
rest:
  - resource: "http://<TRACKER_IP>/api/v1/status"
    scan_interval: 1
    sensor:
      - name: "Solakon PowerTracker IR"
        value_template: "{{ value_json.extracted.instantaneous_power_w }}"
```

Replace `<TRACKER_IP>` with the IP address of your PowerTracker IR.

> **Note**: After adding this configuration, reload the REST integration via Developer Tools → YAML → REST. A full Home Assistant restart is not required.

## Automation Examples

### Battery Power Monitoring
```yaml
automation:
  - alias: "Battery Discharging Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solakon_one_battery_power
        above: 5000  # Alert when discharging more than 5kW
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
