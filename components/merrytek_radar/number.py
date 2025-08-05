import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number
from esphome.const import (CONF_ID, CONF_TYPE,CONF_ADDRESS,CONF_MAX_VALUE,CONF_MIN_VALUE,CONF_STEP,)
from . import merrytek_radar_ns, MerrytekRadar, MerrytekNumber

# Define supported number entities and their function codes
CONF_DETECTION_AREA = "detection_area"
CONF_HOLD_TIME = "hold_time"
CONF_BLOCKING_TIME = "blocking_time"
CONF_LUX_DIFFERENCE_THRESHOLD = "lux_difference_threshold"
CONF_DAYLIGHT_THRESHOLD = "daylight_threshold"
CONF_MERRYTEK_RADAR_ID = "merrytek_radar_id"

NUMBERS = {
    CONF_DETECTION_AREA: 0x05,
    CONF_HOLD_TIME: 0x0D,
    CONF_BLOCKING_TIME: 0x07,
    CONF_LUX_DIFFERENCE_THRESHOLD: 0x0A,
    CONF_DAYLIGHT_THRESHOLD: 0x25,
}

CONFIG_SCHEMA = number.NUMBER_SCHEMA.extend({
    cv.GenerateID(CONF_MERRYTEK_RADAR_ID): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*NUMBERS, lower=True),
    cv.GenerateID(CONF_ID): cv.declare_id(MerrytekNumber),
    cv.Optional(CONF_MIN_VALUE, default=0.0): cv.float_,
    cv.Optional(CONF_MAX_VALUE, default=255.0): cv.float_,
    cv.Optional(CONF_STEP, default=1.0): cv.positive_float,
}).extend(cv.COMPONENT_SCHEMA)
# Generate C++ code
async def to_code(config):
    parent = await cg.get_variable(config[CONF_MERRYTEK_RADAR_ID])
    var = cg.new_Pvariable(config[CONF_ID])
    await number.register_number(
        var,
        config,
        min_value=config[CONF_MIN_VALUE],
        max_value=config[CONF_MAX_VALUE],
        step=config[CONF_STEP],
    )
    await number.register_component(var, config)

    number_type = config[CONF_TYPE]
    function_code = NUMBERS[number_type]
    cg.add(var.set_function_code(function_code))
    cg.add(parent.register_configurable_number(config[CONF_ADDRESS], function_code, var))















