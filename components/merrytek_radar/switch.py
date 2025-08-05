import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_ADDRESS,
)

# Import our custom C++ classes from __init__.py
from . import merrytek_radar_ns, MerrytekRadar, MerrytekSwitch

# Define supported switch entities and their function codes
CONF_LED_INDICATOR = "led_indicator"
CONF_REPORT_QUERY_MODE = "report_query_mode"
CONF_PRESENCE_DETECTION_ENABLE = "presence_detection_enable"
CONF_SINGLE_PERSON_MODE = "single_person_mode"
CONF_LIGHT_SENSING_MODE = "light_sensing_mode"

SWITCHS = {
    CONF_LED_INDICATOR: 0x08,
    CONF_REPORT_QUERY_MODE: 0x22,
    CONF_PRESENCE_DETECTION_ENABLE: 0x28,
    CONF_SINGLE_PERSON_MODE: 0x31,
    CONF_LIGHT_SENSING_MODE: 0x32,
}

# Define the configuration schema for switch entities, updated for the new architecture
PLATFORM_SCHEMA = switch.SWITCH_SCHEMA.extend({
    cv.GenerateID(cg.PARENT_ID): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*SWITCHS, lower=True),
    cv.GenerateID(CONF_ID): cv.declare_id(MerrytekSwitch),
}).extend(cv.PLATFORM_SCHEMA)

# Generate C++ code
async def to_code(config):
    parent = await cg.get_variable(config[cg.PARENT_ID])
    var = cg.new_Pvariable(config[CONF_ID])
    await switch.register_switch(var, config)
    switch_type = config[CONF_TYPE]
    function_code = SWITCHS[switch_type]
    cg.add(var.set_function_code(function_code))
    cg.add(parent.register_configurable_switch(config[CONF_ADDRESS], function_code, var))





