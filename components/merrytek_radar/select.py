import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import select
from esphome.const import CONF_ID, CONF_SENSITIVITY
from . import MerrytekSelect, MerrytekRadar

# Define supported select entities and their function codes
CONF_NEAR_ZONE_SHIELDING = "near_zone_shielding"

SELECTS = {
    CONF_SENSITIVITY: (0x06, ["Low", "High", "Medium"]),
    CONF_NEAR_ZONE_SHIELDING: (0x33, ["0m", "0.6m", "1.2m", "1.6m"]),
}

# Define the configuration schema for select entities
CONFIG_SCHEMA = select.SELECT_SCHEMA.extend({
    cv.GenerateID(CONF_ID): cv.declare_id(MerrytekSelect),
    cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
    cv.Required("type"): cv.one_of(*SELECTS, lower=True),
}).extend(cv.COMPONENT_SCHEMA)

# Generate C++ code
async def to_code(config):
    hub = await cg.get_variable(config["merrytek_radar_id"])
    var = await cg.new_Pvariable(config[CONF_ID])
    
    sensor_type = config["type"]
    function_code, options = SELECTS[sensor_type]
    
    await select.register_select(var, config, options=options)
    await cg.register_component(var, config)
    
    cg.add(hub.register_configurable_select(var, function_code))
