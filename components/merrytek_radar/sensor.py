import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_ADDRESS,
    CONF_ICON,
    CONF_ID,
    CONF_STATE_CLASS,
    CONF_TYPE,
    CONF_UNIT_OF_MEASUREMENT,
    ICON_CHIP,
    STATE_CLASS_MEASUREMENT,
    UNIT_LUX,
)

from . import merrytek_radar_ns, MerrytekRadar

CONF_LIGHT_LEVEL = "light_level"
CONF_DIFFERENCE_VALUE = "difference_value"
CONF_FIRMWARE_VERSION = "firmware_version"
CONF_MERRYTEK_RADAR_ID = "merrytek_radar_id"

SENSORS = {
    CONF_LIGHT_LEVEL: 0x09,
    CONF_DIFFERENCE_VALUE: 0x0A,
    CONF_FIRMWARE_VERSION: 0x17,
}

CONFIG_SCHEMA = sensor.SENSOR_SCHEMA.extend(
    {
        cv.GenerateID(CONF_MERRYTEK_RADAR_ID): cv.use_id(MerrytekRadar),
        cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
        cv.Required(CONF_TYPE): cv.one_of(*SENSORS, lower=True),
        cv.Optional(CONF_STATE_CLASS): cv.enum(sensor.STATE_CLASSES, upper=True),
    }
)

async def to_code(config):
    parent = await cg.get_variable(config[CONF_MERRYTEK_RADAR_ID])

    config_copy = config.copy()
    state_class = config_copy.pop(CONF_STATE_CLASS, None)
    
    var = await sensor.new_sensor(config_copy)

    if state_class is not None:
        cg.add(var.set_state_class(state_class))
    
    sensor_type = config[CONF_TYPE]
    function_code = SENSORS[sensor_type]

    if sensor_type == CONF_LIGHT_LEVEL:
        if CONF_UNIT_OF_MEASUREMENT not in config:
            cg.add(var.set_unit_of_measurement(UNIT_LUX))
        if state_class is None:
            cg.add(var.set_state_class(STATE_CLASS_MEASUREMENT))

    elif sensor_type == CONF_FIRMWARE_VERSION:
        if CONF_ICON not in config:
            cg.add(var.set_icon(ICON_CHIP))

    cg.add(parent.register_configurable_sensor(config[CONF_ADDRESS], function_code, var))
