import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart, switch, binary_sensor, sensor, text_sensor, number, select, button
from esphome.const import CONF_ID, CONF_ADDRESS, CONF_MODEL, CONF_NAME

CODEOWNERS = ["@Pickllo"]
MULTI_CONF = True

merrytek_radar_ns = cg.esphome_ns.namespace("merrytek_radar")
MerrytekRadar = merrytek_radar_ns.class_("MerrytekRadar", cg.PollingComponent, uart.UARTDevice)
MerrytekSwitch = merrytek_radar_ns.class_("MerrytekSwitch", switch.Switch, cg.Component)
MerrytekNumber = merrytek_radar_ns.class_("MerrytekNumber", number.Number, cg.Component)
MerrytekSelect = merrytek_radar_ns.class_("MerrytekSelect", select.Select, cg.Component)
MerrytekButton = merrytek_radar_ns.class_("MerrytekButton", button.Button, cg.Component)
MerrytekSensor = merrytek_radar_ns.class_("MerrytekSensor", sensor.Sensor, cg.Component)
MerrytekTextSensor = merrytek_radar_ns.class_("MerrytekTextSensor", text_sensor.TextSensor, cg.Component)
SelectBehavior = merrytek_radar_ns.enum("SelectBehavior")

MODELS = ["msa237d", "msa236d"]

DEVICE_SCHEMA = cv.Schema({
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_MODEL): cv.one_of(*MODELS, lower=True),
    cv.Required(CONF_NAME): cv.string,
})

CONFIG_SCHEMA = (
    cv.Schema({
        cv.GenerateID(): cv.declare_id(MerrytekRadar),
        cv.Required("devices"): cv.ensure_list(DEVICE_SCHEMA),
    })
    .extend(cv.polling_component_schema("60s"))
    .extend(uart.UART_DEVICE_SCHEMA)
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
    for device_conf in config["devices"]:
        cg.add(var.register_device(
            device_conf[CONF_NAME], 
            device_conf[CONF_ADDRESS], 
            device_conf[CONF_MODEL]
        ))
