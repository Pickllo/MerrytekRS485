[![ESPHome External Component](https://img.shields.io/badge/ESPHome-external_component-blue.svg)](https://esphome.io/components/external_components.html)

This is a custom external component for **ESPHome** to integrate Merrytek radar presence sensors that use the RS485 binary protocol. It provides a comprehensive set of entities to monitor and control the sensor(s) directly from Home Assistant.

This component is designed for robust **multi-device support**, allowing you to control multiple, distinct radar sensors on a single RS485 bus without interference.

## Supported Devices

This component has been developed and tested with the following models:
* **msa237d (Presence Sensor)**
* **msa236d (Motion Sensor)**

It may be compatible with other Merrytek models that use the same RS485 protocol.

## Features

* **Multi-Device Hub:** Manages communication for multiple sensors on one bus.
* **Presence Detection:** `binary_sensor` for occupancy/motion status.
* **Status Reporting:**
    * `text_sensor` to display the device's **firmware version**.
    * `text_sensor` to show the real-time status of the **self-learning** process (e.g., "Learning finished", "Learning failed").
* **Controls:**
    * `switch` entities to toggle the LED, enable/disable detection, etc.
    * `number` inputs to configure `hold_time`.
    * `select` dropdowns for settings like `sensitivity`, `near_zone_shielding`, and model-specific `detection_area`.
    * `button` entities for actions like `factory_reset`, `ignore_distractions`, and to query the `firmware_version`.

## Installation

You can install this component directly from GitHub using the `external_components` feature in your ESPHome YAML configuration.

```yaml
external_components:
  - source:
      type: git
      url: [https://github.com/Pickllo/MerrytekRS485]
      ref: main
    components: [ merrytek_radar ]


```
## Hardware Requirements


* **An ESP32 or ESP8266 board.**
* **An RS485 to TTL converter (e.g., a module based on the MAX485 chip) to interface between the ESP's UART pins and the sensor's RS485 A/B lines.**

## Configuration

Configuration is split into two parts: the main hub component that manages the bus, and the individual entity configurations.

1. Hub Configuration

First, define the UART bus and the merrytek_radar component. This component acts as a hub for all your devices.
Define the UART bus for RS485 communication
YAML

uart:
  - id: uart_485
    tx_pin: 18
    rx_pin: 8
    baud_rate: 9600

Add the main component configuration
YAML
merrytek_radar:
  uart_id: uart_485
  id: merrytek_bus_manager
  
List all devices on the bus
YAML
  devices:
    - name: "Presence"
      address: 0x0000
      model: "msa237d"
    - name: "Motion"
      address: 0xFFFF
      model: "msa236d"

2. Entity Configuration

You can then add entities for each device. All entities require a merrytek_radar_id (pointing to the hub) and the device address.

Binary Sensor

type: presence - The main motion/occupancy sensor.

YAML

binary_sensor:
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Presence"
    address: 0x0000
    type: presence
    device_class: occupancy



Text Sensor

type: firmware_version - Displays the firmware version. Requires the query_firmware_version button to be pressed to update.
type: learning_status - Shows the status of the self-learning feature. (For msa237d)

YAML


text_sensor:
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Presence Firmware Version"
    address: 0x0000
    type: firmware_version
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Presence Learning Status"
    address: 0x0000
    type: learning_status
    icon: mdi:brain



Button

type: factory_reset - Resets the device to factory defaults.
type: flip_status - Inverts the presence detection logic.
type: query_firmware_version - Required to update the firmware_version text sensor.
type: environmental_self_learning - Starts the 6-minute self-learning process. (For msa237d)
type: ignore_distractions - Triggers the "Ignore distractions" function. (For msa237d)

YAML


button:
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Presence Firmware Query"
    address: 0x0000
    type: query_firmware_version



Select

type: sensitivity
type: near_zone_shielding
type: presence_detection_area - For sensors that use distance in meters (e.g., msa237d).
type: motion_detection_area - For sensors that use percentage (e.g., msa236d).

YAML


select:
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Presence Detection Area"
    address: 0x0000
    type: presence_detection_area



Switch

type: led_indicator - Toggles the onboard LED.
type: presence_detection_enable - Enables or disables the sensor.
type: report_query_mode - Switches between active reporting and query-only mode.

Number

type: hold_time - Configures the hold time in seconds.





