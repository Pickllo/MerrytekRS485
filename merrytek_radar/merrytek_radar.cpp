#include "merrytek_radar.h"
#include "esphome/core/log.h"
#include <numeric>

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
static const uint8_t FUNC_ID_EDIT_STATUS = 0x21;
static const uint8_t FUNC_REPORT_QUERY_MODE = 0x22;
static const uint8_t FUNC_FLIP_STATUS = 0x23;
static const uint8_t FUNC_DAYLIGHT_THRESHOLD = 0x25;
static const uint8_t FUNC_PRESENCE_DETECTION_ENABLE = 0x28;
static const uint8_t FUNC_ENVIRONMENTAL_SELF_LEARNING = 0x29;
static const uint8_t FUNC_FACTORY_RESET = 0x30;
static const uint8_t FUNC_SINGLE_PERSON_MODE = 0x31;
static const uint8_t FUNC_LIGHT_SENSING_MODE = 0x32;
static const uint8_t FUNC_NEAR_ZONE_SHIELDING = 0x33;

// --- Frame Constants ---
static const uint8_t FRAME_HEADER = 0x51;
static const uint8_t FRAME_FORMAT = 0x00;
static const uint8_t BASE_FRAME_LENGTH = 6; // Base length without data and CRC

// =================== Component Setup and Loop ===================
void MerrytekRadar::setup() {}

void MerrytekRadar::dump_config() {
  ESP_LOGCONFIG(TAG, "Merrytek Radar:");
  LOG_UART_DEVICE(this);
  ESP_LOGCONFIG(TAG, "  Device ID: 0x%04X", this->device_id_);
  LOG_UPDATE_INTERVAL(this);
  LOG_BINARY_SENSOR("  ", "Presence", this->presence_sensor_);
  LOG_SENSOR("  ", "Light Level", this->light_sensor_);
  // Log other entities...
}

void MerrytekRadar::update() {
  ESP_LOGD(TAG, "Requesting all data...");
  this->send_command(FUNC_READ_ALL);
}

void MerrytekRadar::loop() {
  while (available()) {
    uint8_t byte;
    read_byte(&byte);
    this->rx_buffer_.push_back(byte);
  }

  while (this->rx_buffer_.size() >= 4) {
    if (this->rx_buffer_[0] != FRAME_HEADER) {
      this->rx_buffer_.erase(this->rx_buffer_.begin());
      continue;
    }

    uint8_t payload_len = this->rx_buffer_[3];
    uint8_t total_frame_len = payload_len + 1;
    if (this->rx_buffer_.size() < total_frame_len) {
      return;
    }
    
    std::vector<uint8_t> frame(this->rx_buffer_.begin(), this->rx_buffer_.begin() + total_frame_len);
    uint8_t received_crc = frame.back();
    uint8_t calculated_crc = calculate_crc(frame.data(), payload_len);

    if (received_crc == calculated_crc) {
      uint16_t frame_id = (frame[1] << 8) | frame[2];
      if (this->device_id_ == 0x0000 || frame_id == this->device_id_) {
        this->handle_frame(frame);
      }
    } else {
      ESP_LOGW(TAG, "CRC Check Failed! Got 0x%02X, calculated 0x%02X", received_crc, calculated_crc);
    }
    
    this->rx_buffer_.erase(this->rx_buffer_.begin(), this->rx_buffer_.begin() + total_frame_len);
  }
}

// =================== Frame Handling ===================
void MerrytekRadar::handle_frame(const std::vector<uint8_t> &frame) {
  uint8_t function = frame[5];
  uint8_t data_len = frame[3] - BASE_FRAME_LENGTH;
  const uint8_t *data = frame.data() + BASE_FRAME_LENGTH;

  ESP_LOGD(TAG, "Received frame: function=0x%02X, data_len=%d", function, data_len);

  switch (function) {
    case FUNC_WORK_STATE:
      if (data_len >= 1) {
        if (this->presence_sensor_ != nullptr) this->presence_sensor_->publish_state(data[0] == 1);
        auto it_sw = this->switches_.find(function);
        if (it_sw != this->switches_.end()) it_sw->second->publish_state(data[0] == 1);
      }
      break;
    case FUNC_LIGHT_SENSOR:
      if (this->light_sensor_ != nullptr && data_len >= 2) {
        this->light_sensor_->publish_state((data[0] << 8) | data[1]);
      }
      break;
    case FUNC_FIRMWARE_VERSION:
      if (this->firmware_version_sensor_ != nullptr && data_len >= 3) {
        // Assuming format is three bytes for X.Y.Z
        this->firmware_version_sensor_->publish_state(data[0] + (data[1]/10.0f) + (data[2]/100.0f));
      }
      break;
    case FUNC_DETECTION_AREA:
    case FUNC_BLOCKING_TIME:
    case FUNC_HOLD_TIME:
    case FUNC_DAYLIGHT_THRESHOLD:
    case FUNC_LUX_DIFFERENCE_THRESHOLD: {
      auto it_num = this->numbers_.find(function);
      if (it_num != this->numbers_.end() && data_len >= 1) {
          uint32_t value = 0;
          for(int i=0; i<data_len; ++i) {
            value = (value << 8) | data[i];
          }
          it_num->second->publish_state(value);
      }
      break;
    }
    case FUNC_LED_INDICATOR:
    case FUNC_REPORT_QUERY_MODE:
    case FUNC_PRESENCE_DETECTION_ENABLE:
    case FUNC_SINGLE_PERSON_MODE:
    case FUNC_LIGHT_SENSING_MODE: {
      auto it_sw = this->switches_.find(function);
      if (it_sw != this->switches_.end() && data_len >= 1) {
          it_sw->second->publish_state(data[0] == 1);
      }
      break;
    }
    case FUNC_SENSITIVITY:
    case FUNC_NEAR_ZONE_SHIELDING: {
      auto it_sel = this->selects_.find(function);
      if (it_sel != this->selects_.end() && data_len >= 1) {
        it_sel->second->publish_state(it_sel->second->at(data[0]).value());
      }
      break;
    }
  }
}

// =================== Command Sending ===================
void MerrytekRadar::send_command(uint8_t function, const std::vector<uint8_t> &data) {
  uint8_t payload_len = BASE_FRAME_LENGTH + data.size();
  std::vector<uint8_t> frame;
  frame.reserve(payload_len + 1);

  frame.push_back(FRAME_HEADER);
  frame.push_back((this->device_id_ >> 8) & 0xFF);
  frame.push_back(this->device_id_ & 0xFF);
  frame.push_back(payload_len);
  frame.push_back(FRAME_FORMAT);
  frame.push_back(function);
  frame.insert(frame.end(), data.begin(), data.end());

  frame.push_back(calculate_crc(frame.data(), frame.size()));
  this->write_array(frame);
  this->flush();
}

uint8_t MerrytekRadar::calculate_crc(const uint8_t *data, uint8_t len) {
  return std::accumulate(data, data + len, (uint8_t)0);
}

// =================== Controllable Entity Logic ===================
void MerrytekRadar::register_configurable_number(MerrytekNumber *num, uint8_t fc) { this->numbers_[fc] = num; num->set_parent(this); num->set_function_code(fc); }
void MerrytekRadar::register_configurable_switch(MerrytekSwitch *sw, uint8_t fc) { this->switches_[fc] = sw; sw->set_parent(this); sw->set_function_code(fc); }
void MerrytekRadar::register_configurable_select(MerrytekSelect *sel, uint8_t fc) { this->selects_[fc] = sel; sel->set_parent(this); sel->set_function_code(fc); }
void MerrytekRadar::register_configurable_button(MerrytekButton *btn, uint8_t fc, const std::vector<uint8_t>& data) { this->buttons_[fc] = btn; btn->set_parent(this); btn->set_function_code(fc); btn->set_data(data); }

void MerrytekNumber::control(float value) {
  this->publish_state(value);
  uint32_t int_val = static_cast<uint32_t>(value);
  std::vector<uint8_t> data;

  if (int_val > 0xFFFFFF) data.push_back((int_val >> 24) & 0xFF);
  if (int_val > 0xFFFF) data.push_back((int_val >> 16) & 0xFF);
  if (int_val > 0xFF) data.push_back((int_val >> 8) & 0xFF);
  data.push_back(int_val & 0xFF);

  this->parent_->send_command(this->function_code_, data);
}

void MerrytekSwitch::write_state(bool state) {
  this->publish_state(state);
  this->parent_->send_command(this->function_code_, {static_cast<uint8_t>(state)});
}

void MerrytekSelect::control(const std::string &value) {
    this->publish_state(value);
    auto index = this->index_of(value);
    if(index.has_value()){
        this->parent_->send_command(this->function_code_, {static_cast<uint8_t>(index.value())});
    }
}

void MerrytekButton::press_action() { this->parent_->send_command(this->function_code_, this->data_); }

}  // namespace merrytek_radar
}  // namespace esphome