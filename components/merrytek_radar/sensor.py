import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_ID,
    CONF_FIRMWARE_VERSION,
    ICON_CHIP,
    STATE_CLASS_MEASUREMENT,
    UNIT_LUX,
)
from . import MerrytekRadar

# Define our custom sensor types as strings
CONF_LIGHT_LEVEL = "light_level"
CONF_DIFFERENCE_VALUE = "difference_value"

# Map the custom types to their function codes
SENSORS = {
    CONF_LIGHT_LEVEL: 0x09,
    CONF_DIFFERENCE_VALUE: 0x0A,
    CONF_FIRMWARE_VERSION: 0x17,
}

# Define the configuration schema for sensors
CONFIG_SCHEMA = sensor.SENSOR_SCHEMA.extend({
    cv.GenerateID(CONF_ID): cv.declare_id(sensor.Sensor),
    cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
    cv.Required("type"): cv.one_of(*SENSORS, lower=True),
}).extend(cv.COMPONENT_SCHEMA)

# Generate C++ code
async def to_code(config):
    hub = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    await sensor.register_sensor(var, config)

    sensor_type = config["type"]
    if sensor_type == CONF_LIGHT_LEVEL:
        cg.add(hub.set_light_sensor(var))
        cg.add(var.set_unit_of_measurement(UNIT_LUX))
        cg.add(var.set_state_class(STATE_CLASS_MEASUREMENT))
    elif sensor_type == CONF_DIFFERENCE_VALUE:
        cg.add(hub.set_difference_value_sensor(var))
        cg.add(var.set_unit_of_measurement(UNIT_LUX))
    elif sensor_type == CONF_FIRMWARE_VERSION:
        cg.add(hub.set_firmware_version_sensor(var))
        cg.add(var.set_icon(ICON_CHIP))
