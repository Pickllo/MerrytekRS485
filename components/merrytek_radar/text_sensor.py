import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_ADDRESS,
    ICON_CHIP,
    CONF_ICON,
)
from . import merrytek_radar_ns, MerrytekRadar, MerrytekTextSensor

CONF_MERRYTEK_RADAR_ID = "merrytek_radar_id"
CONF_LEARNING_STATUS = "learning_status"

TYPES = ["firmware_version", CONF_LEARNING_STATUS]

FUNCTION_CODES = {
    "firmware_version": 0x17,
}
CONFIG_SCHEMA = text_sensor.text_sensor_schema(
    MerrytekTextSensor,
    icon=ICON_CHIP
).extend({
    cv.GenerateID(CONF_MERRYTEK_RADAR_ID): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*TYPES, lower=True),
})

async def to_code(config):
    parent = await cg.get_variable(config[CONF_MERRYTEK_RADAR_ID])
    var = cg.new_Pvariable(config[CONF_ID])
    
    await text_sensor.register_text_sensor(var, config)
    await cg.register_component(var, config)

    cg.add(var.set_parent(parent))
    cg.add(var.set_address(config[CONF_ADDRESS]))

    if config[CONF_TYPE] == CONF_LEARNING_STATUS:
        cg.add(parent.register_learning_status_text_sensor(config[CONF_ADDRESS], var))
    else:
        function_code = FUNCTION_CODES[config[CONF_TYPE]]
        cg.add(var.set_function_code(function_code))
        cg.add(parent.register_configurable_text_sensor(config[CONF_ADDRESS], function_code, var))
