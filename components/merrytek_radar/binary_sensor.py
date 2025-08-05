import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_ADDRESS,
    CONF_PARENT_ID,
    DEVICE_CLASS_OCCUPANCY,
)
from . import MerrytekRadar, merrytek_radar_ns

# Define supported binary sensors and their function codes
CONF_PRESENCE = "presence"
BINARY_SENSORS = {
    CONF_PRESENCE: 0x03,
}

PLATFORM_SCHEMA = binary_sensor.BINARY_SENSOR_SCHEMA.extend({
    cv.GenerateID(cCONF_PARENT_ID): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*BINARY_SENSORS, lower=True),
}).extend(cv.PLATFORM_SCHEMA)
# Generate C++ code
async def to_code(config):
    parent = await cg.get_variable(config[CONF_PARENT_ID])
    var = await binary_sensor.new_binary_sensor(config)
    sensor_type = config[CONF_TYPE]
    if sensor_type == CONF_PRESENCE:
        cg.add(var.set_device_class(DEVICE_CLASS_OCCUPANCY))
    cg.add(parent.register_binary_sensor(config[CONF_ADDRESS], sensor_type, var))



