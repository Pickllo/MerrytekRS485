import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import select
from esphome.const import (CONF_ID, CONF_TYPE,CONF_ADDRESS,)
from esphome.core import CORE
from . import merrytek_radar_ns, MerrytekRadar, MerrytekSelect

# Define supported select entities and their function codes
CONF_NEAR_ZONE_SHIELDING = "near_zone_shielding"
CONF_SENSITIVITY = "sensitivity"
CONF_PRESENCE_DETECTION_AREA = "presence_detection_area"
CONF_MOTION_DETECTION_AREA = "motion_detection_area"
CONF_MERRYTEK_RADAR_ID = "merrytek_radar_id"
SELECTS = {
    CONF_SENSITIVITY: (0x06, ["Low", "High", "Medium"]),
    CONF_NEAR_ZONE_SHIELDING: (0x33, ["0m", "0.6m", "1.2m", "1.6m"]),
    CONF_PRESENCE_DETECTION_AREA: (0x05, ["0m", "0.5m", "1m", "1.5m", "2m", "2.5m", "3m", "3.5m", "4m"]),
    CONF_MOTION_DETECTION_AREA: (0x05, ["0%", "25%", "50%", "75%", "100%"]),
}

CONFIG_SCHEMA = select.SELECT_SCHEMA.extend({
    cv.GenerateID(CONF_MERRYTEK_RADAR_ID): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required("type"): cv.one_of(*SELECTS, lower=True),
    cv.GenerateID(CONF_ID): cv.declare_id(MerrytekSelect),
})

# Generate C++ code
async def to_code(config):
    parent = await cg.get_variable(config[CONF_MERRYTEK_RADAR_ID])
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    select_type = config["type"]
    function_code, options = SELECTS[select_type]
    await select.register_select(var, config, options=options)
    cg.add(var.set_function_code(function_code))
    behavior = SelectBehavior.SEND_INDEX
    if select_type == CONF_MOTION_DETECTION_AREA:
        behavior = SelectBehavior.SEND_PERCENTAGE_VALUE
    cg.add(parent.register_configurable_select(config[CONF_ADDRESS], function_code, var, behavior))
