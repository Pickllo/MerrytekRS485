import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button
from esphome.const import CONF_ID
from . import MerrytekRadar

# Define supported button entities and their function codes
CONF_FACTORY_RESET = "factory_reset"
CONF_ENVIRONMENTAL_SELF_LEARNING = "environmental_self_learning"
CONF_ID_EDIT_ENABLE = "id_edit_enable"
CONF_FLIP_STATUS = "flip_status"

BUTTONS = {
    CONF_FACTORY_RESET: (0x30, [0x01]),
    CONF_ENVIRONMENTAL_SELF_LEARNING: (0x29, [0x01]),
    CONF_ID_EDIT_ENABLE: (0x21, [0x01]),
    CONF_FLIP_STATUS: (0x23, [0x01]),
}

# Define the configuration schema for button entities
CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ID): cv.declare_id(button.Button),
        cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
        cv.Required("type"): cv.one_of(*BUTTONS, lower=True),
    }
).extend(button.BUTTON_SCHEMA)

# Generate C++ code
async def to_code(config):
    hub = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    await button.register_button(var, config)

    sensor_type = config["type"]
    function_code, data = BUTTONS[sensor_type]
    
    # Correct syntax for creating a std::vector<uint8_t>
    data_vector = cg.std_vector.template(cg.uint8)(data)
    
    cg.add(hub.register_configurable_button(var, function_code, data_vector))
