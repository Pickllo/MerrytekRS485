import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart, switch, number, select, button
from esphome.const import CONF_ID

# Declare all the components our hub depends on
DEPENDENCIES = ['uart', 'binary_sensor', 'sensor', 'number', 'switch', 'select', 'button']

# Declare the component's namespace
CODEOWNERS = ["@Pickllo"]
merrytek_radar_ns = cg.esphome_ns.namespace("merrytek_radar")

# Declare the HUB class - REMOVED PollingComponent
MerrytekRadar = merrytek_radar_ns.class_(
    "MerrytekRadar", cg.Component, uart.UARTDevice
)

# Declare the custom entity classes that live in the C++ code
MerrytekSwitch = merrytek_radar_ns.class_("MerrytekSwitch", switch.Switch, cg.Component)
MerrytekNumber = merrytek_radar_ns.class_("MerrytekNumber", number.Number, cg.Component)
MerrytekSelect = merrytek_radar_ns.class_("MerrytekSelect", select.Select, cg.Component)
MerrytekButton = merrytek_radar_ns.class_("MerrytekButton", button.Button, cg.Component)

# Define our custom configuration key
CONF_DEVICE_ID = "device_id"

# Define the configuration schema for the main hub - REMOVED polling_component_schema
CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(MerrytekRadar),
            cv.Required(CONF_DEVICE_ID): cv.hex_uint16_t,
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(uart.UART_DEVICE_SCHEMA)
)

# Define the coroutine to generate the C++ code for the main hub
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
    cg.add(var.set_device_id(config[CONF_DEVICE_ID]))
