import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import (
    CONF_ID,
    DEVICE_CLASS_OCCUPANCY,
)
from . import MerrytekRadar, merrytek_radar_ns

# Define supported binary sensors and their function codes
CONF_PRESENCE = "presence"
BINARY_SENSORS = {
    CONF_PRESENCE: 0x03,
}

# Define the configuration schema for binary sensors
CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ID): cv.declare_id(binary_sensor.BinarySensor),
        cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
        cv.Required("type"): cv.one_of(*BINARY_SENSORS, lower=True),
    }
).extend(binary_sensor.BINARY_SENSOR_SCHEMA)

# Generate C++ code
async def to_code(config):
    hub = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    await binary_sensor.register_binary_sensor(var, config)

    sensor_type = config["type"]
    if sensor_type == CONF_PRESENCE:
        cg.add(hub.set_presence_binary_sensor(var))
        cg.add(var.set_device_class(DEVICE_CLASS_OCCUPANCY))