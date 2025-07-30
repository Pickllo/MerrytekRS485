import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID
from esphome.core import coroutine_with_priority

# Declare all the components our hub depends on
DEPENDENCIES = ['uart', 'binary_sensor', 'sensor', 'number', 'switch', 'select', 'button']

# Declare the component's namespace
CODEOWNERS = ["@Pickllo"]
merrytek_radar_ns = cg.esphome_ns.namespace("merrytek_radar")
MerrytekRadar = merrytek_radar_ns.class_(
    "MerrytekRadar", cg.PollingComponent, uart.UARTDevice
)

# Define our custom configuration key
CONF_DEVICE_ID = "device_id"

# Define the configuration schema
CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(MerrytekRadar),
            cv.Required(CONF_DEVICE_ID): cv.hex_uint16_t,
        }
    )
    .extend(cv.polling_component_schema("60s"))
    .extend(uart.UART_DEVICE_SCHEMA)
)

# Define the coroutine to generate the C++ code
@coroutine_with_priority(40.0)
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
    cg.add(var.set_device_id(config[CONF_DEVICE_ID]))
