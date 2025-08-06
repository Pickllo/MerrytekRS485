import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_ADDRESS,
    DEVICE_CLASS_ILLUMINANCE,
    STATE_CLASS_MEASUREMENT,
    UNIT_LUX,
    ICON_LIGHTBULB,
)

from . import merrytek_radar_ns, MerrytekRadar

MerrytekSensor = merrytek_radar_ns.class_("MerrytekSensor", sensor.Sensor, cg.Component)

TYPES = ["light_level"]

FUNCTION_CODES = {
    "light_level": 0x01,
}

CONFIG_SCHEMA = sensor.sensor_schema(
    unit_of_measurement=UNIT_LUX,
    device_class=DEVICE_CLASS_ILLUMINANCE,
    state_class=STATE_CLASS_MEASUREMENT,
    icon=ICON_LIGHTBULB,
).extend({
    cv.GenerateID(): cv.declare_id(MerrytekSensor),
    cv.Required("merrytek_radar_id"): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*TYPES, lower=True),
})

async def to_code(config):
    parent = await cg.get_variable(config["merrytek_radar_id"])
    var = cg.new_Pvariable(config[CONF_ID])
    await sensor.register_sensor(var, config)
    cg.add(var.set_parent(parent))
    cg.add(var.set_address(config[CONF_ADDRESS]))
    function_code = FUNCTION_CODES[config[CONF_TYPE]]
    cg.add(var.set_function_code(function_code))

    # Register this sensor with the parent hub
    cg.add(parent.register_configurable_sensor(config[CONF_ADDRESS], function_code, var))
