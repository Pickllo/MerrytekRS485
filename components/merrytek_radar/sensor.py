import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_ADDRESS,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_DEVICE_CLASS,
    CONF_STATE_CLASS,
    DEVICE_CLASS_ILLUMINANCE,
    STATE_CLASS_MEASUREMENT,
    UNIT_LUX,
)
from . import MerrytekRadar, merrytek_radar_ns

TYPES = ["light_level"]

CONFIG_SCHEMA = sensor.sensor_schema(
    unit_of_measurement=str,
    device_class=str,
    state_class=str,
).extend({
    cv.GenerateID(): cv.declare_id(sensor.Sensor),
    cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*TYPES, lower=True),
})

async def to_code(config):
    parent = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    await sensor.register_sensor(var, config)

    if config[CONF_TYPE] == "light_level":
        cg.add(var.set_parent(parent))
        cg.add(var.set_address(config[CONF_ADDRESS]))
        cg.add(var.set_value_type(0))
        cg.add(var.set_device_class(DEVICE_CLASS_ILLUMINANCE))
        cg.add(var.set_unit_of_measurement(UNIT_LUX))
        cg.add(var.set_state_class(STATE_CLASS_MEASUREMENT))
        cg.add(parent.register_sensor_listener(var))
