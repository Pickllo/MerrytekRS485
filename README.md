# ESPHome Merrytek Radar Presence Sensor

[![ESPHome External Component](https://img.shields.io/badge/ESPHome-external_component-blue.svg)](https://esphome.io/components/external_components.html)

This is a custom external component for **ESPHome** to integrate Merrytek radar presence sensors that use the RS485 binary protocol. It provides a comprehensive set of entities to monitor and control the sensor directly from Home Assistant.

## Supported Devices

This component was developed based on the protocol for Merrytek radar sensors communicating over RS485. It should be compatible with models that follow the documented binary protocol.

## Features

* **Presence Detection:** `binary_sensor` for occupancy status.
* **Sensors:** Read the ambient `light_level` and other values.
* **Controls:**
    * `switch` entities to toggle the LED, enable/disable presence detection, etc.
    * `number` inputs to configure `hold_time`, `daylight_threshold`, and more.
    * `select` dropdowns for settings like `sensitivity` and `near-zone_shielding`.
    * `button` entities for actions like `factory_reset`.

## Installation

You can install this component directly from GitHub using the `external_components` feature in your ESPHome YAML configuration.

```yaml
external_components:
  - source:
      type: git
      url: [https://github.com/Pickllo/MerrytekRS485](https://github.com/Pickllo/MerrytekRS485)
      ref: main # Or a specific tag/commit
    components: [ merrytek_radar ]
```

## Hardware Requirements

1.  An ESP32 or ESP8266 board.
2.  An **RS485 to TTL converter** (e.g., a module based on the MAX485 chip) to interface between the ESP's UART pins and the sensor's RS485 A/B lines.
3.  A pin on the ESP to control the DE/RE (Transmit Enable) pin on the RS485 converter.

## Configuration Example

Here is a full example configuration for the component and its various entities.

```yaml
# 1. Define the UART bus for RS485 communication
uart:
  - id: uart_bus
    tx_pin: GPIO17
    rx_pin: GPIO16
    baud_rate: 9600
    tx_enable_pin: GPIO4 # Pin to control DE/RE on the MAX485 adapter

# 2. Add the component configuration
merrytek_radar:
  - uart_id: uart_bus
    update_interval: 10s
    device_id: 0x0000 # Use your sensor's specific ID if not default
    id: my_radar

# 3. Define the entities for your sensor
binary_sensor:
  - platform: merrytek_radar
    merrytek_radar_id: my_radar
    type: presence
    name: "Radar Presence"

sensor:
  - platform: merrytek_radar
    merrytek_radar_id: my_radar
    type: light_level
    name: "Radar Light Level"

switch:
  - platform: merrytek_radar
    merrytek_radar_id: my_radar
    type: led_indicator
    name: "Radar LED Indicator"
  - platform: merrytek_radar
    merrytek_radar_id: my_radar
    type: presence_detection_enable
    name: "Radar Presence Detection"

number:
  - platform: merrytek_radar
    merrytek_radar_id: my_radar
    type: hold_time
    name: "Radar Hold Time"
    unit_of_measurement: "s"
    min_value: 3
    max_value: 7200
    step: 1

select:
  - platform: merrytek_radar
    merrytek_radar_id: my_radar
    type: sensitivity
    name: "Radar Sensitivity"

button:
  - platform: merrytek_radar
    merrytek_radar_id: my_radar
    type: factory_reset
    name: "Radar Factory Reset"
```
