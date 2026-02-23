import logging # TODO
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import DOMAIN, CONF_ADDRESS


BUTTON_DEFS = [
    ("fs20_dummy_test", "FS20 dummy test entiy", 25),
]

_LOGGER = logging.getLogger(__name__) # TODO

async def async_setup_entry(hass, entry, async_add_entities):
    """Register all FS20PCS button entities."""
    handler = hass.data[DOMAIN]["handler"]
    housecode = hass.data[DOMAIN]["housecode"]

    entities = []

    for key, name, cmd in BUTTON_DEFS:
        entities.append(
            FS20PCSButton(
                name=name,
                key=key,
                cmd=cmd,
                handler=handler,
                housecode=housecode,
                entry_id=entry.entry_id,
            )
        )

    async_add_entities(entities, True)


class FS20PCSButton(ButtonEntity):
    """A single FS20 button entity."""

    def __init__(self, name, key, cmd, handler, housecode, entry_id):
        self._attr_name = name
        self._attr_unique_id = f"fs20pcs_{key}"
        self._cmd = cmd
        self._handler = handler
        self._housecode_str = housecode
        self._entry_id = entry_id
        self._attr_entity_category = EntityCategory.CONFIG

        # Default fallback address
        self._default_address = "1111"

    
    # -----------------------------
    # ADDRESS HANDLING (OPTIONS)
    # -----------------------------
    @property
    def address(self):
        """Return the configured address (or default)."""
        registry = async_get_entity_registry(self.hass)
        entry = registry.async_get(self.entity_id)
        if entry and "address" in entry.options:
            _LOGGER.debug(f"FS20PCSButton-> address: {entry.options["address"]}")
            return entry.options["address"]
        else:
            _LOGGER.error("FS20PCSButton-> No address found")

        return self._default_address

    # Show address as attribute for debugging
    @property
    def extra_state_attributes(self):
        return {"address": self.address}

    # -----------------------------
    # MAIN ACTION
    # -----------------------------
    async def async_press(self):
        hc1, hc2 = self._handler.convert_housecode(self._housecode_str)
        adr = self._handler.convert_address(self.address)
        self._handler.send(hc1, hc2, adr, self._cmd)
