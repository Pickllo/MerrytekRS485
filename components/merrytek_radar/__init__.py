import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID, CONF_ADDRESS, CONF_MODEL, CONF_NAME

# Declare the component's namespace
CODEOWNERS = ["@Pickllo"]
merrytek_radar_ns = cg.esphome_ns.namespace("merrytek_radar")
MerrytekRadar = merrytek_radar_ns.class_(
    "MerrytekRadar", cg.PollingComponent, uart.UARTDevice
)

MODELS = ["msa237d", "msa236d"]

DEVICE_SCHEMA = cv.Schema({
    cv.Required(CONF_ADDRESS): cv.hex_uint16_t,
    cv.Required(CONF_MODEL): cv.one_of(*MODELS, lower=True),
    cv.Required(CONF_NAME): cv.string,
})
# Define the configuration schema
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(MerrytekRadar),
    
    # The new, required way to define devices
    cv.Required("devices"): cv.ensure_list(DEVICE_SCHEMA),

}).extend(cv.polling_component_schema("60s")).extend(uart.UART_DEVICE_SCHEMA)


# Define the coroutine to generate the C++ code
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
    for device_conf in config["devices"]:
        cg.add(var.register_device(device_conf[CONF_NAME], device_conf[CONF_ADDRESS], device_conf[CONF_MODEL], ))
