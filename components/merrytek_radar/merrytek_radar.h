#pragma once
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/switch/switch.h"
#include "esphome/components/number/number.h"
#include "esphome/components/select/select.h"
#include "esphome/components/button/button.h"
#include <map>
#include <string>
#include <vector>

namespace esphome {
namespace merrytek_radar {
class MerrytekRadar; 
struct RadarDevice {
  std::string name;
  uint16_t address;
  std::string model;
  binary_sensor::BinarySensor *presence_sensor_{nullptr};
  std::map<uint8_t, sensor::Sensor *> sensors_;
  std::map<uint8_t, text_sensor::TextSensor *> text_sensors_; 
  std::map<uint8_t, number::Number *> numbers_;
  std::map<uint8_t, switch_::Switch *> switches_;
  std::map<uint8_t, select::Select *> selects_;
  std::map<uint8_t, button::Button *> buttons_;
};

class MerrytekRadar : public PollingComponent, public uart::UARTDevice {
 public:
  void setup() override;
  void loop() override;
  void update() override;
  void dump_config() override;

  void register_device(const std::string &name, uint16_t address, const std::string &model);
  void register_presence_sensor(uint16_t address, binary_sensor::BinarySensor *sensor);
  void register_configurable_sensor(uint16_t address, uint8_t function_code, sensor::Sensor *sensor);
  void register_configurable_text_sensor(uint16_t address, uint8_t function_code, text_sensor::TextSensor *sensor);
  void register_configurable_number(uint16_t address, uint8_t function_code, number::Number *num);
  void register_configurable_switch(uint16_t address, uint8_t function_code, switch_::Switch *sw);
  void register_configurable_select(uint16_t address, uint8_t function_code, select::Select *sel);
  void register_configurable_button(uint16_t address, uint8_t function_code, button::Button *btn, const std::vector<uint8_t> &data);
  
  void send_command_to_device(uint16_t address, uint8_t function_code, const std::vector<uint8_t> &data = {});

 protected:
  void handle_frame(const std::vector<uint8_t> &frame);
  uint8_t calculate_crc(const uint8_t *data, uint8_t len);

  std::map<uint16_t, RadarDevice> devices_;
  std::vector<uint8_t> rx_buffer_;
};

class MerrytekSensor : public sensor::Sensor, public Component {
public:
    void set_parent(MerrytekRadar *parent) { this->parent_ = parent; }
    void set_address(uint16_t address) { this->address_ = address; }
    void set_function_code(uint8_t code) { this->function_code_ = code; }
protected:
    MerrytekRadar *parent_;
    uint16_t address_;
    uint8_t function_code_;
};

class MerrytekTextSensor : public text_sensor::TextSensor, public Component {
public:
    void set_parent(MerrytekRadar *parent) { this->parent_ = parent; }
    void set_address(uint16_t address) { this->address_ = address; }
    void set_function_code(uint8_t code) { this->function_code_ = code; }
protected:
    MerrytekRadar *parent_;
    uint16_t address_;
    uint8_t function_code_;
};

class MerrytekNumber : public number::Number, public Component {
 public:
  void control(float value) override;
  void set_parent_and_address(MerrytekRadar *parent, uint16_t address) { this->parent_ = parent; this->address_ = address; }
  void set_function_code(uint8_t code) { this->function_code_ = code; }
 protected:
  MerrytekRadar *parent_;
  uint16_t address_;
  uint8_t function_code_;
};

class MerrytekSwitch : public switch_::Switch, public Component {
 public:
  void write_state(bool state) override;
  void set_parent_and_address(MerrytekRadar *parent, uint16_t address) { this->parent_ = parent; this->address_ = address; }
  void set_function_code(uint8_t code) { this->function_code_ = code; }
 protected:
  MerrytekRadar *parent_;
  uint16_t address_;
  uint8_t function_code_;
};

class MerrytekSelect : public select::Select, public Component {
 public:
  enum SelectBehavior {
    SEND_INDEX,         
    SEND_PERCENTAGE_VALUE 
  };
  void control(const std::string &value) override;
  void set_parent_and_address(MerrytekRadar *parent, uint16_t address) { this->parent_ = parent; this->address_ = address; }
  void set_function_code(uint8_t code) { this->function_code_ = code; }
  void set_behavior(SelectBehavior behavior) { this->behavior_ = behavior; }
  SelectBehavior get_behavior() const { return this->behavior_; }
 protected:
  MerrytekRadar *parent_;
  uint16_t address_;
  uint8_t function_code_;
  SelectBehavior behavior_{SEND_INDEX};
};

class MerrytekButton : public button::Button, public Component {
 public:
  void press_action() override;
  void set_parent_and_address(MerrytekRadar *parent, uint16_t address) { this->parent_ = parent; this->address_ = address; }
  void set_function_code(uint8_t code) { this->function_code_ = code; }
  void set_data(const std::vector<uint8_t>& data) { this->data_ = data; }
 protected:
  MerrytekRadar *parent_;
  uint16_t address_;
  uint8_t function_code_;
  std::vector<uint8_t> data_;
};
} // namespace merrytek_radar
} // namespace esphome


