#include "merrytek_radar.h"
#include "esphome/core/log.h"
#include <numeric>
#include <map>
#include <algorithm>

namespace esphome {
namespace merrytek_radar {

static const char *const TAG = "merrytek_radar";

// --- Function Codes ---
static const uint8_t FUNC_READ_ALL = 0x00;
static const uint8_t FUNC_WORK_STATE = 0x03;
static const uint8_t FUNC_DETECTION_AREA = 0x05;
static const uint8_t FUNC_SENSITIVITY = 0x06;
static const uint8_t FUNC_BLOCKING_TIME = 0x07;
static const uint8_t FUNC_LED_INDICATOR = 0x08;
static const uint8_t FUNC_LIGHT_SENSOR = 0x09;
static const uint8_t FUNC_LUX_DIFFERENCE_THRESHOLD = 0x0A;
static const uint8_t FUNC_HOLD_TIME = 0x0D;
static const uint8_t FUNC_FIRMWARE_VERSION = 0x17;
static const uint8_t FUNC_DEVICE_ID = 0x18;
static const uint8_t FUNC_DAYLIGHT_COMPENSATION = 0x20;
static const uint8_t FUNC_ID_EDIT_STATUS = 0x21;
static const uint8_t FUNC_REPORT_QUERY_MODE = 0x22;
static const uint8_t FUNC_FLIP_STATUS = 0x23;
static const uint8_t FUNC_DAYLIGHT_THRESHOLD = 0x25;
static const uint8_t FUNC_SENSOR_ACTIVATION = 0x26;
static const uint8_t FUNC_PRESENCE_DETECTION_ENABLE = 0x28;
static const uint8_t FUNC_ENVIRONMENTAL_SELF_LEARNING = 0x29;
static const uint8_t FUNC_FACTORY_RESET = 0x30;
static const uint8_t FUNC_SINGLE_PERSON_MODE = 0x31;
static const uint8_t FUNC_LIGHT_SENSING_MODE = 0x32;
static const uint8_t FUNC_NEAR_ZONE_SHIELDING = 0x33;

static const uint8_t FRAME_HEADER = 0x51;

void MerrytekRadar::register_device(const std::string &name, uint16_t address, const std::string &model) {
  ESP_LOGD(TAG, "Registering device: %s (Address: 0x%04X, Model: %s)", name.c_str(), address, model.c_str());
  RadarDevice new_device;
  new_device.name = name;
  new_device.address = address;
  new_device.model = model;
  this->devices_[address] = new_device;
}

void MerrytekRadar::dump_config() {
  ESP_LOGCONFIG(TAG, "Merrytek Radar Bus Manager:");
  if (this->devices_.empty()) {
    ESP_LOGCONFIG(TAG, "  No devices configured.");
    return;
  }
  ESP_LOGCONFIG(TAG, "  Configured Devices:");
  for (auto const &[address, device] : this->devices_) {
    ESP_LOGCONFIG(TAG, "    - Device: '%s'", device.name.c_str());
    ESP_LOGCONFIG(TAG, "      Address: 0x%04X", device.address);
    ESP_LOGCONFIG(TAG, "      Model: %s", device.model.c_str());
  }
}

void MerrytekRadar::setup() {
  ESP_LOGI(TAG, "Initializing Merrytek Radar Bus Manager...");
}

void MerrytekRadar::update() {
  // Polling logic can be added here if needed.
}

void MerrytekRadar::loop() {
  while (this->available()) {
    uint8_t byte;
    this->read_byte(&byte);
    this->rx_buffer_.push_back(byte);
  }

  while (this->rx_buffer_.size() >= 4) {
    if (this->rx_buffer_[0] != FRAME_HEADER) {
      this->rx_buffer_.erase(this->rx_buffer_.begin());
      continue;
    }

    uint8_t payload_len = this->rx_buffer_[3];
    if (payload_len < 5) {
      this->rx_buffer_.erase(this->rx_buffer_.begin());
      continue;
    }
    uint8_t total_frame_len = payload_len + 1;
    if (this->rx_buffer_.size() < total_frame_len) {
      return;
    }

    std::vector<uint8_t> frame(this->rx_buffer_.begin(), this->rx_buffer_.begin() + total_frame_len);
    uint8_t received_crc = frame.back();
    uint8_t calculated_crc = this->calculate_crc(frame.data(), frame.size() - 1);

    if (received_crc == calculated_crc) {
      this->handle_frame(frame);
    } else {
      ESP_LOGW(TAG, "CRC Check Failed! Got 0x%02X, calculated 0x%02X", received_crc, calculated_crc);
    }

    this->rx_buffer_.erase(this->rx_buffer_.begin(), this->rx_buffer_.begin() + total_frame_len);
  }
}

void MerrytekRadar::handle_frame(const std::vector<uint8_t> &frame) {
  uint16_t frame_id = (frame[1] << 8) | frame[2];
  auto it = this->devices_.find(frame_id);
  if (it == this->devices_.end()) {
    ESP_LOGV(TAG, "Ignoring frame from unconfigured address 0x%04X", frame_id);
    return;
  }
  RadarDevice &device = it->second;
  uint8_t function = frame[4];
  uint8_t payload_len = frame[3];
  uint8_t data_len = payload_len - 5;
  const uint8_t *data = frame.data() + 5;

  ESP_LOGD(TAG, "Received frame for device '%s' (Address: 0x%04X, Function: 0x%02X)",
           device.name.c_str(), device.address, function);
  
  if (function == FUNC_DETECTION_AREA) {
    auto it_sel = device.selects_.find(function);
    if (it_sel != device.selects_.end() && data_len >= 1) {
      auto *merrytek_sel = static_cast<MerrytekSelect *>(it_sel->second);
      uint8_t received_value = data[0];

      if (merrytek_sel->get_behavior() == MerrytekSelect::SEND_PERCENTAGE_VALUE) {
        if (received_value == 0 || received_value == 25 || received_value == 50 || received_value == 75 || received_value == 100) {
            uint8_t target_percentage = received_value; 
            bool found = false;
            for (size_t i = 0; i < merrytek_sel->size(); i++) {
                optional<std::string> option_str_opt = merrytek_sel->at(i);
                if (option_str_opt.has_value()) {
                    std::string option_str = option_str_opt.value();
                    char* end;
                    long option_val = strtol(option_str.c_str(), &end, 10);
                    if (end != option_str.c_str() && option_val == target_percentage) {
                        merrytek_sel->publish_state(option_str);
                        found = true;
                        break;
                    }
                }
            }
            if (!found) {
                ESP_LOGW(TAG, "Received valid percentage %d for '%s', but could not find a matching option string.",
                          received_value, merrytek_sel->get_name().c_str());
            }
        } else {
            ESP_LOGD(TAG, "Ignoring detection area broadcast with value %d for device '%s'",
                      received_value, merrytek_sel->get_name().c_str());
        }
      } else {
        if (received_value < merrytek_sel->size()) {
          merrytek_sel->publish_state(merrytek_sel->at(received_value).value());
        }
      }
    }
    return;
  }
  if (device.model == "msa236d") {
    switch (function) {
      case FUNC_WORK_STATE:
        if (data_len >= 1 && device.presence_sensor_ != nullptr) {
          bool is_present = (data[0] == 0x02);
          device.presence_sensor_->publish_state(is_present);
        }
        break;
      case FUNC_LIGHT_SENSOR: {
        auto it_sens = device.sensors_.find(function);
        if (it_sens != device.sensors_.end() && data_len >= 1) {
          uint32_t value = 0;
          for (int i = 0; i < data_len; ++i) {
            value = (value << 8) | data[i];
          }
          it_sens->second->publish_state(value);
        }
        break;
      }
      case FUNC_FIRMWARE_VERSION: {
        auto it_txt_sens = device.text_sensors_.find(function);
        if (it_txt_sens != device.text_sensors_.end() && data_len >= 1) {
          std::string version_string(reinterpret_cast<const char*>(data), data_len);
          it_txt_sens->second->publish_state(version_string);
        }
        break;
      }
      case FUNC_HOLD_TIME: {
        auto it_num = device.numbers_.find(function);
        if (it_num != device.numbers_.end() && data_len >= 1) {
          uint32_t value = 0;
          for (int i = 0; i < data_len; ++i) { value = (value << 8) | data[i]; }
          it_num->second->publish_state(value);
        }
        break;
      }
      case FUNC_LED_INDICATOR:
      case FUNC_REPORT_QUERY_MODE:
      case FUNC_PRESENCE_DETECTION_ENABLE: {
        auto it_sw = device.switches_.find(function);
        if (it_sw != device.switches_.end() && data_len >= 1) {
          it_sw->second->publish_state(data[0] == 1);
        }
        break;
      }
    }
  } else if (device.model == "msa237d") {
    switch (function) {
      case FUNC_WORK_STATE:
        if (data_len >= 1 && device.presence_sensor_ != nullptr) {
          device.presence_sensor_->publish_state(data[0] == 0x02);
        }
        break;
      case FUNC_LIGHT_SENSOR:
      case FUNC_LUX_DIFFERENCE_THRESHOLD: {
        auto it_sens = device.sensors_.find(function);
        if (it_sens != device.sensors_.end() && data_len >= 1) {
          uint32_t value = 0;
          for (int i = 0; i < data_len; ++i) { value = (value << 8) | data[i]; }
          it_sens->second->publish_state(value);
        }
        break;
      }
      case FUNC_FIRMWARE_VERSION: {
        auto it_txt_sens = device.text_sensors_.find(function);
        if (it_txt_sens != device.text_sensors_.end() && data_len >= 1) {
          std::string version_string(reinterpret_cast<const char*>(data), data_len);
          it_txt_sens->second->publish_state(version_string);
        }
        break;
      }
      case FUNC_LED_INDICATOR:
      case FUNC_REPORT_QUERY_MODE:
      case FUNC_PRESENCE_DETECTION_ENABLE: {
        auto it_sw = device.switches_.find(function);
        if (it_sw != device.switches_.end() && data_len >= 1) {
          it_sw->second->publish_state(data[0] == 1);
        }
        break;
      }
      case FUNC_SENSITIVITY:
      case FUNC_NEAR_ZONE_SHIELDING: {
        auto it_sel = device.selects_.find(function);
        if (it_sel != device.selects_.end() && data_len >= 1) {
          if (data[0] < it_sel->second->size()) {
            it_sel->second->publish_state(it_sel->second->at(data[0]).value());
          }
        }
        break;
      }
    }
  }
}

void MerrytekRadar::send_command_to_device(uint16_t address, uint8_t function_code, const std::vector<uint8_t> &data) {
  uint8_t payload_len = 5 + data.size();
  std::vector<uint8_t> frame;
  frame.reserve(payload_len + 1);

  frame.push_back(FRAME_HEADER);
  frame.push_back((address >> 8) & 0xFF);
  frame.push_back(address & 0xFF);
  frame.push_back(payload_len);
  frame.push_back(function_code);
  frame.insert(frame.end(), data.begin(), data.end());

  frame.push_back(this->calculate_crc(frame.data(), frame.size()));

  this->write_array(frame);
  this->flush();
}

uint8_t MerrytekRadar::calculate_crc(const uint8_t *data, uint8_t len) {
  return std::accumulate(data, data + len, (uint8_t)0);
}

void MerrytekRadar::register_presence_sensor(uint16_t address, binary_sensor::BinarySensor *sensor) {
  auto it = this->devices_.find(address);
  if (it != this->devices_.end()) {
    it->second.presence_sensor_ = sensor;
  }
}

void MerrytekRadar::register_configurable_number(uint16_t address, uint8_t function_code, number::Number *num) {
  auto it = this->devices_.find(address);
  if (it != this->devices_.end()) {
    it->second.numbers_[function_code] = num;
    static_cast<MerrytekNumber *>(num)->set_parent_and_address(this, address);
  }
}

void MerrytekRadar::register_configurable_switch(uint16_t address, uint8_t function_code, switch_::Switch *sw) {
  auto it = this->devices_.find(address);
  if (it != this->devices_.end()) {
    it->second.switches_[function_code] = sw;
    static_cast<MerrytekSwitch *>(sw)->set_parent_and_address(this, address);
  }
}

void MerrytekRadar::register_configurable_select(uint16_t address, uint8_t function_code, select::Select *sel, SelectBehavior behavior) {
  auto it = this->devices_.find(address);
  if (it != this->devices_.end()) {
    it->second.selects_[function_code] = sel;
    auto *merrytek_sel = static_cast<MerrytekSelect *>(sel);
    merrytek_sel->set_parent_and_address(this, address);
    merrytek_sel->set_behavior(behavior); 
  }
}

void MerrytekRadar::register_configurable_button(uint16_t address, uint8_t function_code, button::Button *btn, const std::vector<uint8_t> &data) {
  auto it = this->devices_.find(address);
  if (it != this->devices_.end()) {
    it->second.buttons_[function_code] = btn;
    auto *merrytek_btn = static_cast<MerrytekButton *>(btn);
    merrytek_btn->set_parent_and_address(this, address);
    merrytek_btn->set_function_code(function_code);
    merrytek_btn->set_data(data);
  }
}

void MerrytekRadar::register_configurable_sensor(uint16_t address, uint8_t function_code, sensor::Sensor *sensor) {
  auto it = this->devices_.find(address);
  if (it != this->devices_.end()) {
    it->second.sensors_[function_code] = sensor;
  }
}

void MerrytekRadar::register_configurable_text_sensor(uint16_t address, uint8_t function_code, text_sensor::TextSensor *sensor) {
  auto it = this->devices_.find(address);
  if (it != this->devices_.end()) {
    it->second.text_sensors_[function_code] = sensor;
  }
}

void MerrytekNumber::control(float value) {
  this->publish_state(value);
  uint32_t int_val = static_cast<uint32_t>(value);
  std::vector<uint8_t> data;
  if (int_val > 0xFFFF) data.push_back((int_val >> 16) & 0xFF);
  if (int_val > 0xFF) data.push_back((int_val >> 8) & 0xFF);
  data.push_back(int_val & 0xFF);
  this->parent_->send_command_to_device(this->address_, this->function_code_, data);
}

void MerrytekSwitch::write_state(bool state) {
  this->publish_state(state);
  this->parent_->send_command_to_device(this->address_, this->function_code_, {static_cast<uint8_t>(state)});
}

void MerrytekSelect::control(const std::string &value) {
  this->publish_state(value);
  std::vector<uint8_t> data;

  switch (this->behavior_) {
    case SEND_PERCENTAGE_VALUE: {
      char* end;
      long percentage_val = strtol(value.c_str(), &end, 10);
      if (end != value.c_str()) { 
        data.push_back(static_cast<uint8_t>(percentage_val));
      } else {
        ESP_LOGE(TAG, "Cannot convert select option '%s' to a number.", value.c_str());
      }
      break;
    }
    case SEND_INDEX:
    default: {
      auto index = this->index_of(value);
      if (index.has_value()) {
        data.push_back(static_cast<uint8_t>(*index));
      }
      break;
    }
  }

  if (!data.empty()) {
    this->parent_->send_command_to_device(this->address_, this->function_code_, data);
  }
}

void MerrytekButton::press_action() {
  this->parent_->send_command_to_device(this->address_, this->function_code_, this->data_);
}

}  // namespace merrytek_radar
}  // namespace esphome






