import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_ADDRESS,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_ICON,
    CONF_STATE_CLASS,
    UNIT_LUX,
    ICON_CHIP,
    STATE_CLASS_MEASUREMENT,
)

from . import merrytek_radar_ns, MerrytekRadar

CONF_LIGHT_LEVEL = "light_level"
CONF_DIFFERENCE_VALUE = "difference_value"
CONF_FIRMWARE_VERSION = "firmware_version"

SENSORS = {
    CONF_LIGHT_LEVEL: 0x09,
    CONF_DIFFERENCE_VALUE: 0x0A,
    CONF_FIRMWARE_VERSION: 0x17,
}

PLATFORM_SCHEMA = sensor.SENSOR_PLATFORM_SCHEMA.extend({
    cv.GenerateID(cg.PARENT_ID): cv.use_id(MerrytekRadar),
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_TYPE): cv.one_of(*SENSORS, lower=True),
})

async def to_code(config):
    parent = await cg.get_variable(config[cg.PARENT_ID])
    var = await sensor.new_sensor(config)
    sensor_type = config[CONF_TYPE]
    function_code = SENSORS[sensor_type]
    if sensor_type == CONF_LIGHT_LEVEL:
        if CONF_UNIT_OF_MEASUREMENT not in config:
            cg.add(var.set_unit_of_measurement(UNIT_LUX))
        if CONF_STATE_CLASS not in config:
            cg.add(var.set_state_class(STATE_CLASS_MEASUREMENT))
    elif sensor_type == CONF_FIRMWARE_VERSION:
        if CONF_ICON not in config:
            cg.add(var.set_icon(ICON_CHIP))
    cg.add(parent.register_configurable_sensor(config[CONF_ADDRESS], function_code, var))
