import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_HOUSECODE
from .usb_handler import FS20USBHandler

# ----------------------------------------
# Config-Flow for entering the Housecode
# ----------------------------------------
class FS20PCSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                handler = FS20USBHandler()
                handler.convert_housecode(user_input[CONF_HOUSECODE])
                return self.async_create_entry(
                    title="FS20 PCS",
                    data=user_input
                )
            except Exception:
                errors["base"] = "invalid_housecode"

        schema = vol.Schema({
            vol.Required(CONF_HOUSECODE): str
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
