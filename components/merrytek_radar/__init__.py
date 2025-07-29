import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_UART_ID
from esphome.core import coroutine_with_priority

# Declare the component's namespace
CODEOWNERS = ["@Pickllo"]
merrytek_radar_ns = cg.esphome_ns.namespace("merrytek_radar")
MerrytekRadar = merrytek_radar_ns.class_(
    "MerrytekRadar", cg.PollingComponent, cg.UARTComponent
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
    .extend(cv.UART_DEVICE_SCHEMA)
)

# Define the coroutine to generate the C++ code
@coroutine_with_priority(40.0)
async def to_code(config):
    uart_device = await cg.get_variable(config[CONF_UART_ID])
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await cg.register_uart_device(var, config)
    cg.add(var.set_device_id(config[CONF_DEVICE_ID]))

    # Ensure this component is set up after the UART bus
    cg.add_dependency(uart_device, var)
