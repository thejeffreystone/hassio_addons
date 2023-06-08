# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.21]
- Updating default Channel at init. Thanks @slappare and @th3dll for spotting it

## [0.1.20]
- Fixing Wind speed unit of measurement
- Fixing Rain sensor unit of measurement

## [0.1.18b]
- Fixed issue where debug and whitelist_enable are incorrectly marked as being on when they are off.
- When whitelist_enabled is on, any Device ID and Models not in whitelist will be listed in the log. This will 
  only be listed once, until the add-on is restarted. Debug not required.
  * whitelist only prevents Home Assistant Auto Discovery - devices will still show up in MQTT *
- If no instance is found, device will be assigned an instance of 0 to try and fix that 
  add-on crash when no instance is found. 
- Fix bug where whitelist_enabled is sometimes ignored. 
- Switch to an actual logger for log messages. 
- Added device class to sensors
- Removed any "unit of measurement" that was empty to prevent errors after 2023.5 update
- state_class is now defined for each device instead of globally set to measurement to reduce errors after 2023.5 update. 
- auto discovery can now be turned off in the configuration for anyone that doesn't want devices to be auto added to home assistant
- Some bug fixes by @doozers-do
  - Channel now defaults to A instead of 0
  - Channel sensor now defined as a enum device with options as A, B, or C


## [0.1.17b]
- Bug fix with expire that didn't get caught in my local test

## [0.1.16b]
- Bump to make sure latest 433_rtl is grabbed.
- Brings in parity with Acurite Version

## [0.1.14b]
- Bump to make sure latest 433_rtl is grabbed.

## [0.1.13b]
### Bug fixing
- Removed null device ID from new channel definition

## [0.1.12b]
### Changed
- Added Definition for Temp from Thermopro TP12

## [0.1.11]
### Changed
- Adding back in frequnecey And adding Whitelist

## [0.1.9]
### Changed
- Updated Autodiscovery to handle model values that were not in manufacturer-model format. 


## [0.1.8]
### Added
- Added last_seen enity which should be the last time Home Assistant saw an update from 
  rtl_433.
- Added Freq definition to autodiscovery which reports device frequency
- Added channel definition to autodiscovery which report device channel 
- Added wind_max_km_h definition to autodiscovery

## [0.1.7]
### Added
- Added consumption definition for gas meters
- Update rtl_433 to version 21.12-63-g2d041b5d

## [0.1.6]
### Added
- Added port to the config so you can use mwtt ports other than 1883

## [0.1.5]
### Added
- Added new definition for light_klx value from Brersser 7in1

## [0.1.4]
### Changed
- More Rain gauge bug fixes.

## [0.1.3]
### Changed
- Updated Rain Gauge unit of measurements in device definition.

## [0.1.2]
### Added
- Units to the config so you can set to metric or customary/imperial  

## [0.1.0]
### Added
- Initial Release - Testing a multipurpose add-on... 
