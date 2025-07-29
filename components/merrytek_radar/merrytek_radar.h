#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/number/number.h"
#include "esphome/components/switch/switch.h"
#include "esphome/components/select/select.h"
#include "esphome/components/button/button.h"
#include <vector>
#include <map>

namespace esphome {
namespace merrytek_radar {

class MerrytekRadar; // Forward declaration

// Custom classes to handle callbacks from ESPHome entities
class MerrytekNumber : public number::Number, public Component {
 public:
  void control(float value) override;
  void set_parent(MerrytekRadar *parent) { this->parent_ = parent; }
  void set_function_code(uint8_t code) { this->function_code_ = code; }
 protected:
  MerrytekRadar *parent_;
  uint8_t function_code_;
};

class MerrytekSwitch : public switch_::Switch, public Component {
 public:
  void write_state(bool state) override;
  void set_parent(MerrytekRadar *parent) { this->parent_ = parent; }
  void set_function_code(uint8_t code) { this->function_code_ = code; }
 protected:
  MerrytekRadar *parent_;
  uint8_t function_code_;
};

class MerrytekSelect : public select::Select, public Component {
 public:
  void control(const std::string &value) override;
  void set_parent(MerrytekRadar *parent) { this->parent_ = parent; }
  void set_function_code(uint8_t code) { this->function_code_ = code; }
 protected:
  MerrytekRadar *parent_;
  uint8_t function_code_;
};

class MerrytekButton : public button::Button, public Component {
 public:
  void press_action() override;
  void set_parent(MerrytekRadar *parent) { this->parent_ = parent; }
  void set_function_code(uint8_t code) { this->function_code_ = code; }
  void set_data(const std::vector<uint8_t>& data) { this->data_ = data; }
 protected:
  MerrytekRadar *parent_;
  uint8_t function_code_;
  std::vector<uint8_t> data_;
};


// Main Component Class
class MerrytekRadar : public PollingComponent, public uart::UARTDevice {
 public:
  void setup() override;
  void loop() override;
  void update() override;
  void dump_config() override;

  void set_device_id(uint16_t device_id) { this->device_id_ = device_id; }
  
  // Setters for read-only entities
  void set_presence_binary_sensor(binary_sensor::BinarySensor *sensor) { this->presence_sensor_ = sensor; }
  void set_light_sensor(sensor::Sensor *sensor) { this->light_sensor_ = sensor; }
  void set_difference_value_sensor(sensor::Sensor *sensor) { this->difference_value_sensor_ = sensor; }
  void set_firmware_version_sensor(sensor::Sensor *sensor) { this->firmware_version_sensor_ = sensor; }

  // Registration for controllable entities
  void register_configurable_number(MerrytekNumber *num, uint8_t function_code);
  void register_configurable_switch(MerrytekSwitch *sw, uint8_t function_code);
  void register_configurable_select(MerrytekSelect *sel, uint8_t function_code);
  void register_configurable_button(MerrytekButton *btn, uint8_t function_code, const std::vector<uint8_t>& data);
  
  // Public method to send commands from child entities
  void send_command(uint8_t function, const std::vector<uint8_t> &data = {});

 protected:
  void handle_frame(const std::vector<uint8_t> &frame);
  static uint8_t calculate_crc(const uint8_t *data, uint8_t len);
  
  uint16_t device_id_{0x0000};
  std::vector<uint8_t> rx_buffer_;

  // Entity pointers
  binary_sensor::BinarySensor *presence_sensor_{nullptr};
  sensor::Sensor *light_sensor_{nullptr};
  sensor::Sensor *difference_value_sensor_{nullptr};
  sensor::Sensor *firmware_version_sensor_{nullptr};
  std::map<uint8_t, number::Number *> numbers_;
  std::map<uint8_t, switch_::Switch *> switches_;
  std::map<uint8_t, select::Select *> selects_;
  std::map<uint8_t, button::Button *> buttons_;
};

}  // namespace merrytek_radar
}  // namespace esphome