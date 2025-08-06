import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_ID, CONF_TYPE, CONF_ADDRESS
from . import MerrytekRadar

TYPES = ["firmware_version"]

CONFIG_SCHEMA = text_sensor.TEXT_SENSOR_SCHEMA.extend({
    cv.GenerateID(): cv.declare_id(text_sensor.TextSensor),
    cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*TYPES, lower=True),
})

async def to_code(config):
    parent = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    await text_sensor.register_text_sensor(var, config)

    if config[CONF_TYPE] == "firmware_version":
        cg.add(var.set_parent(parent))
        cg.add(var.set_address(config[CONF_ADDRESS]))
        cg.add(var.set_value_type(1)) 
        cg.add(parent.register_text_sensor_listener(var))
