import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_ADDRESS,
    ICON_CHIP,
)

from . import merrytek_radar_ns, MerrytekRadar

MerrytekTextSensor = merrytek_radar_ns.class_("MerrytekTextSensor", text_sensor.TextSensor, cg.Component)

TYPES = ["firmware_version"]

FUNCTION_CODES = {
    "firmware_version": 0x17,
}

CONFIG_SCHEMA = text_sensor.TEXT_SENSOR_SCHEMA.extend({
    cv.GenerateID(): cv.declare_id(MerrytekTextSensor),
    cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*TYPES, lower=True),
    cv.Optional(ICON): ICON_CHIP,
})

async def to_code(config):
    parent = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    await text_sensor.register_text_sensor(var, config)
    cg.add(var.set_parent(parent))
    cg.add(var.set_address(config[CONF_ADDRESS]))
    function_code = FUNCTION_CODES[config[CONF_TYPE]]
    cg.add(var.set_function_code(function_code))
    cg.add(parent.register_configurable_text_sensor(config[CONF_ADDRESS], function_code, var))
