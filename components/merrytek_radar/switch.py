import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch
from esphome.const import CONF_ID
from . import MerrytekSwitch, MerrytekRadar

# Define supported switch entities and their function codes
CONF_LED_INDICATOR = "led_indicator"
CONF_WORK_STATE_OVERRIDE = "work_state_override"
CONF_REPORT_QUERY_MODE = "report_query_mode"
CONF_PRESENCE_DETECTION_ENABLE = "presence_detection_enable"
CONF_SINGLE_PERSON_MODE = "single_person_mode"
CONF_LIGHT_SENSING_MODE = "light_sensing_mode"

SWITCHES = {
    CONF_LED_INDICATOR: 0x08,
    CONF_WORK_STATE_OVERRIDE: 0x03,
    CONF_REPORT_QUERY_MODE: 0x22,
    CONF_PRESENCE_DETECTION_ENABLE: 0x28,
    CONF_SINGLE_PERSON_MODE: 0x31,
    CONF_LIGHT_SENSING_MODE: 0x32,
}

# Define the configuration schema for switch entities
CONFIG_SCHEMA = switch.SWITCH_SCHEMA.extend({
    cv.GenerateID(CONF_ID): cv.declare_id(MerrytekSwitch),
    cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
    cv.Required("type"): cv.one_of(*SWITCHES, lower=True),
}).extend(cv.COMPONENT_SCHEMA)

# Generate C++ code
async def to_code(config):
    hub = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    await switch.register_switch(var, config)
    await cg.register_component(var, config)

    sensor_type = config["type"]
    function_code = SWITCHES[sensor_type]
    cg.add(hub.register_configurable_switch(var, function_code))
