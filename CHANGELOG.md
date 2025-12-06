# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CHANGELOG.md file to track version history and changes
- GitHub labels configuration for better issue classification

### Changed
- Enhanced documentation for entity terminology and capabilities

## [1.0.0] - 2024-12-06

### Added
- ✨ **Device Control Entities**: Control your Solakon ONE device directly from Home Assistant
  - EPS Output Mode control (Disable/EPS/UPS) (#65)
  - Remote Control Mode with 9 operating modes
  - Battery SoC limits (Minimum/Maximum/OnGrid)
  - Remote Active/Reactive Power control
  - Remote timeout settings
- 📊 **New Sensors**: Added control status sensors to monitor current device settings
  - EPS Output Mode status
  - Battery SoC limit settings
  - Remote control status and commands
  - Network status
  - Battery State of Health sensor (#65)
- 🔧 **Improved Energy Dashboard Integration**: Comprehensive documentation for battery integration workaround
- 📖 **Documentation Updates**: Accurate Energy Dashboard integration guide with step-by-step battery setup

### Fixed
- Fixed misleading documentation about Grid Import/Export sensors (not currently supported)
- Corrected Energy Dashboard integration instructions

### Infrastructure
- Release Drafter workflow for automated release notes
- GitHub workflows for hassfest and ruff linting

## [0.1.0] - Initial Release

### Added
- Initial release with basic monitoring capabilities
- Real-time monitoring of all inverter parameters
- PV string monitoring (voltage, current, power)
- Battery management (SOC, power, voltage, current, temperature)
- Energy statistics (total and daily generation)
- Temperature monitoring
- Alarm and status monitoring
- Power factor and grid frequency monitoring
- Full UI configuration support
- Configurable update intervals
- Energy Dashboard compatibility (solar production)
- HACS support

[Unreleased]: https://github.com/solakon-de/solakon-one-homeassistant/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/solakon-de/solakon-one-homeassistant/releases/tag/v1.0.0
[0.1.0]: https://github.com/solakon-de/solakon-one-homeassistant/releases/tag/v0.1.0
