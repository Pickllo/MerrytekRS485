import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number
from esphome.const import (
    CONF_ID,
    CONF_MAX_VALUE,
    CONF_MIN_VALUE,
    CONF_STEP,
    UNIT_EMPTY,
)
from . import MerrytekRadar

# Define supported number entities and their function codes
CONF_DETECTION_AREA = "detection_area"
CONF_HOLD_TIME = "hold_time"
CONF_BLOCKING_TIME = "blocking_time"
CONF_LUX_DIFFERENCE_THRESHOLD = "lux_difference_threshold"
CONF_DAYLIGHT_THRESHOLD = "daylight_threshold"

NUMBERS = {
    CONF_DETECTION_AREA: 0x05,
    CONF_HOLD_TIME: 0x0D,
    CONF_BLOCKING_TIME: 0x07,
    CONF_LUX_DIFFERENCE_THRESHOLD: 0x0A,
    CONF_DAYLIGHT_THRESHOLD: 0x25,
}

# Define the configuration schema for number entities
# This now correctly includes min_value, max_value, and step as optional keys
CONFIG_SCHEMA = number.NUMBER_SCHEMA.extend({
    cv.GenerateID(CONF_ID): cv.declare_id(number.Number),
    cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
    cv.Required("type"): cv.one_of(*NUMBERS, lower=True),
    cv.Optional(CONF_MIN_VALUE): cv.float_,
    cv.Optional(CONF_MAX_VALUE): cv.float_,
    cv.Optional(CONF_STEP): cv.positive_float,
}).extend(cv.COMPONENT_SCHEMA)


# Generate C++ code
async def to_code(config):
    hub = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    
    # Let the register_number helper use the values from the config automatically
    await number.register_number(var, config)

    sensor_type = config["type"]
    function_code = NUMBERS[sensor_type]
    cg.add(hub.register_configurable_number(var, function_code))
