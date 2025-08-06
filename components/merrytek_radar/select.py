import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import select
from esphome.const import (CONF_ID, CONF_TYPE,CONF_ADDRESS,CONF_OPTIONS,)
from . import merrytek_radar_ns, MerrytekRadar, MerrytekSelect

# Define supported select entities and their function codes
CONF_NEAR_ZONE_SHIELDING = "near_zone_shielding"
CONF_SENSITIVITY= "sensitivity" 
CONF_DETECTION_AREA= "detection_area" 
CONF_MERRYTEK_RADAR_ID = "merrytek_radar_id"

SELECTS = {
    CONF_SENSITIVITY: (0x06, ["Low", "High", "Medium"]),
    CONF_NEAR_ZONE_SHIELDING: (0x33, ["0m", "0.6m", "1.2m", "1.6m"]),
    CONF_DETECTION_AREA: (0x05, None), # Options will be set dynamically below
}

CONFIG_SCHEMA = select.SELECT_SCHEMA.extend({
    cv.GenerateID(CONF_MERRYTEK_RADAR_ID): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*SELECTS, lower=True),
    cv.GenerateID(CONF_ID): cv.declare_id(MerrytekSelect),
})

# Generate C++ code
async def to_code(config):
    parent = await cg.get_variable(config[CONF_MERRYTEK_RADAR_ID])
    var = cg.new_Pvariable(config[CONF_ID])
    select_type = config[CONF_TYPE]
    function_code, options = SELECTS[select_type]
    if options is None:
        address = config[CONF_ADDRESS]
        device_model = ""
        for device in parent.config["devices"]:
            if device[CONF_ADDRESS] == address:
                device_model = device[CONF_MODEL]
                break      
        if not device_model:
            raise cv.Invalid(f"Could not find a device with address {address} in the merrytek_radar configuration.")
        if device_model == "msa236d":
            options = ["0%", "25%", "50%", "75%", "100%"]
        else: 
            options = ["0m", "0.5m", "1m", "1.5m", "2m", "2.5m", "3m", "3.5m", "4m"]
    await select.register_select(var, config, options=options)
    await cg.register_component(var, config)
    cg.add(var.set_function_code(function_code))
    cg.add(parent.register_configurable_select(config[CONF_ADDRESS], function_code, var))










