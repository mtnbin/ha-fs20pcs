import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_ADDRESS


class FS20PCSOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}

        entity_registry = er.async_get(self.hass)
        entries = er.async_entries_for_config_entry(
            entity_registry, self.config_entry.entry_id
        )

        # Take first entity to show current value
        current_address = ""
        if entries and "address" in entries[0].options:
            current_address = entries[0].options["address"]

        if user_input is not None:
            addr = user_input[CONF_ADDRESS].strip()
            if len(addr) != 4 or not addr.isdigit():
                errors["base"] = "invalid_address"
            else:
                # Update options for *all* FS20 buttons
                for ent in entries:
                    entity_registry.async_update_entity(
                        ent.entity_id,
                        options={CONF_ADDRESS: addr}
                    )

                return self.async_create_entry(title="", data={})

        schema = vol.Schema({
            vol.Required(CONF_ADDRESS, default=current_address): str
        })

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
