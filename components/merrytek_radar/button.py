import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button
from esphome.const import (CONF_ID, CONF_TYPE,CONF_ADDRESS,)
from . import merrytek_radar_ns, MerrytekRadar, MerrytekButton

# Define supported button entities and their function codes
CONF_FACTORY_RESET = "factory_reset"
CONF_ENVIRONMENTAL_SELF_LEARNING = "environmental_self_learning"
CONF_ID_EDIT_ENABLE = "id_edit_enable"
CONF_FLIP_STATUS = "flip_status"
CONF_MERRYTEK_RADAR_ID = "merrytek_radar_id"

BUTTONS = {
    CONF_FACTORY_RESET: (0x30, [0x01]),
    CONF_ENVIRONMENTAL_SELF_LEARNING: (0x29, [0x01]), # Default action, can be changed via lambda
    CONF_ID_EDIT_ENABLE: (0x21, [0x01]),
    CONF_FLIP_STATUS: (0x23, [0x01]),
}

PLATFORM_SCHEMA = button.BUTTON_SCHEMA.extend({
    cv.GenerateID(CONF_MERRYTEK_RADAR_ID): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*BUTTONS, lower=True),
    cv.GenerateID(CONF_ID): cv.declare_id(MerrytekButton),
}).extend(cv.PLATFORM_SCHEMA)
async def to_code(config):
    parent = await cg.get_variable(config[CONF_MERRYTEK_RADAR_ID])
    var = cg.new_Pvariable(config[CONF_ID])
    await button.register_button(var, config)

    button_type = config[CONF_TYPE]
    function_code, data = BUTTONS[button_type]
    
    cg.add(var.set_data(cg.std_vector(data, type=cg.uint8)))
    
    cg.add(parent.register_configurable_button(config[CONF_ADDRESS], function_code, var))




