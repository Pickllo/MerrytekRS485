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
 
## Pre-Installation: Device Addressing

Before connecting your sensors to the ESP32, you must ensure they are addressed correctly.

**Single Sensor:** If you are only using one sensor, no setup is needed. You can use the default address 0x0000.

**Multiple Sensors:** You must assign a unique address to each sensor (see guide at the bottom) before connecting them to the main bus. Do not use 0x0000 for any of them as it is a broadcast address. Doing so will cause inaccurate device management.

**WARNING**: If multiple sensors use the same address on the same RS485 line, data collisions will occur and the system will not function.

## Hardware Requirements


* **An ESP32 or ESP8266 board.**
* **An RS485 to TTL converter (e.g., a module based on the MAX485 chip) to interface between the ESP's UART pins and the sensor's RS485 A/B lines.(I used a Kincony board, which comes equipped with A/B lines)**
## Installation

1. Define Hub & Hardware

Add the external component, configure your UART pins, and list your physical devices in your ESPHome configuration.

```yaml
external_components:
  - source:
      type: git
      url: [https://github.com/Pickllo/MerrytekRS485]
      ref: main
    components: [ merrytek_radar ]

#Configure UART (Change pins to match your board!)
uart:
  id: uart_485
  tx_pin: 17
  rx_pin: 16
  baud_rate: 9600
  stop_bits: 1

# Define the Hub and Hardware List
merrytek_radar:
  uart_id: uart_485
  id: merrytek_bus_manager
  devices:
    - name: "Living Room"
      address: 0x0001
      model: "msa237d"
    - name: "Kitchen"
      address: 0x0002
      model: "msa237d"

```

2. Import Entities

 **Quick Start (Recommended)**

The easiest way to use this component is via Remote Packages. This automatically creates all switches, sensors, and sliders for your devices without you needing to write hundreds of lines of YAML.

Use the packages configuration to load the interface for each device.
```yaml
packages:
  merrytek_sensors:
    url: [https://github.com/Pickllo/MerrytekRS485]
    ref: main
    files:
      # --- Device 1 ---
      - path: merrytek.yaml
        vars:
          dev_name: "Living Room"         # Prefix for Home Assistant Entities
          dev_addr: "0x0001"              # Must match address in Step 1
          hub_id: merrytek_bus_manager    # Must match ID in Step 1
      
      # --- Device 2 ---
      - path: merrytek.yaml
        vars:
          dev_name: "Kitchen"
          dev_addr: "0x0002"
          hub_id: merrytek_bus_manager

```

**Manual Configuration (Reference)**
If you prefer to manually configure specific entities (or want to know all available types), here is the complete list of options.

Binary Sensor
* type: presence - The main motion/occupancy sensor.

```YAML
binary_sensor:
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Presence"
    address: 0x0000
    type: presence
    device_class: occupancy
```


Text Sensor
* type: firmware_version - Displays the firmware version. Requires the query_firmware_version button to be pressed to update.
* type: learning_status - Shows the status of the self-learning feature. (For msa237d)

```YAML
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
```


Button
* type: factory_reset - Resets the device to factory defaults.
* type: flip_status - Inverts the presence detection logic.
* type: query_firmware_version - Required to update the firmware_version text sensor.
* type: environmental_self_learning - Starts the 6-minute self-learning process. (For msa237d)
* type: ignore_distractions - Triggers the "Ignore distractions" function. (For msa237d)

```YAML
button:
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Presence Firmware Query"
    address: 0x0000
    type: query_firmware_version
```


Select
* type: sensitivity
* type: near_zone_shielding
* type: presence_detection_area - For sensors that use distance in meters (e.g., msa237d).
* type: motion_detection_area - For sensors that use percentage (e.g., msa236d).

```YAML
select:
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Presence Detection Area"
    address: 0x0000
    type: presence_detection_area
```
Switch
* type: led_indicator - Toggles the onboard LED.
* type: presence_detection_enable - Enables or disables the sensor.
* type: report_query_mode - Switches between active reporting and query-only mode.
```yaml
select:
 - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Motion LED Indicator"
    address: 0xFFFF
    type: led_indicator
```
Number
* type: hold_time - Configures the hold time in seconds.
```yaml
number:
  - platform: merrytek_radar
    merrytek_radar_id: merrytek_bus_manager
    name: "Motion Hold Time"
    address: 0xFFFF
    type: hold_time
    min_value: 3
    max_value: 7200
    step: 1
    unit_of_measurement: "s"
```

## Troubleshooting

1. "Component not found: file"
This error occurs if you use the wrong indentation or syntax in the packages section. Ensure you are using the files: list format shown in the Quick Start guide above.

2. Sensors Unavailable
Ensure your UART pins are correct. Do not use pins shared with I2C (often GPIO 8 and 18 on S3 boards) or pins involved in the boot process.

3. Address Conflicts
You must physically set the RS485 address on the sensor (via dip switches or a handheld programmer) before using this component. This component talks to the address, it does not set it.

## Guide to configure Merrytek Sensor Address

1. Prerequisites

Hardware:

* Merrytek Sensor
* 12/24V DC Power Supply Unit (PSU)
* USB-to-RS485 Adapter (A/B)

Software:

* RealTerm (or any other software that allows you to communicate with your serial port)


2. Hardware Setup

* Power: Connect the Sensor to the 12V PSU.
* Data: Connect the Sensor signal wires to the USB-to-RS485 adapter:
Sensor A -> Adapter A+
Sensor B -> Adapter B-
* PC: Plug the USB adapter into your computer and note the COM Port number in Device Manager.

3. Software Configuration (RealTerm)

Open RealTerm.
Display Tab: Set to Hex (Space), Half Duplex, Data: 0xA5 0x5A.
Port Tab - Configure as follows:
Baud : 9600
Parity : None
Data Bits : 8
Stop Bits : 1
Flow Control : None
Port : [Select your COM Port]

Click Open to initialize.

4. Execution Procedure

Step 1: Verify Connection
Send the following command to check the current address:
Command: 0x51 0x00 0x00 0x06 0x00 0x18 0x6F
Expected Result: Data starting with A7 (e.g., A7 00 00 07 18 00 00 C6).

Step 2: Enter Setting Mode
Press the button on the Merrytek device once.
Indicator: The light should flash continuously.

Step 3: Enable Write Permissions
Send the command to unlock editing:
Command: 0x51 0x00 0x00 0x06 0x21 0x01 0x79

Step 4: Set New Address
Send the write command. Replace [Address] and [Checksum] with your specific values.
Command: 0x51 0x00 0x00 0x07 0x18 0x00 [Address] [Checksum]
(Note: Address range is 00-63 (Hex). Refer to the calculated address list for the correct checksum).

Step 5: Confirm Change
Repeat Step 1 to ensure the sensor returns the new address.

