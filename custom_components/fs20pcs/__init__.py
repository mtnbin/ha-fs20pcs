from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
import logging

from .const import DOMAIN
from .usb_handler import FS20USBHandler

_LOGGER = logging.getLogger(__name__)   # <-- Logger definiert


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    handler = FS20USBHandler()
    handler.open()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["handler"] = handler
    hass.data[DOMAIN]["housecode"] = entry.data["housecode"]

    # ---------------------------------------------------------
    # Neuen Service registrieren: fs20pcs.send
    # ---------------------------------------------------------
    async def handle_send(call: ServiceCall):
        address = call.data.get("address")
        try:
            command = int(call.data.get("command"))
        except (TypeError, ValueError):
            raise ValueError("'command' muss eine ganze Zahl sein.")

        # USB-Handler holen
        usb = hass.data[DOMAIN]["handler"]

        # Housecode umrechnen
        hc1, hc2 = usb.convert_housecode(hass.data[DOMAIN]["housecode"])

        # Adresse konvertieren (STRING wie "1234" → Byte)
        adr = usb.convert_address(str(address))

        # KORREKTES LOGGING
        _LOGGER.debug(
            f"FS20PCS send: HC1={hc1}, HC2={hc2}, ADR={adr}, CMD={command}"
        )

        # Senden
        await hass.async_add_executor_job(
            usb.send,
            hc1,
            hc2,
            adr,
            command,
            0   # ext=0
        )

    hass.services.async_register(
        DOMAIN,            # = "fs20pcs"
        "send",            # neuer Dienstname
        handle_send
    )

    # ---------------------------------------------------------
    # Weiterleitung der Button-Entities
    # ---------------------------------------------------------
    await hass.config_entries.async_forward_entry_setups(entry, ["button"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["button"])
    return unload_ok


from .options_flow import FS20PCSOptionsFlowHandler

async def async_get_options_flow(config_entry):
    return FS20PCSOptionsFlowHandler(config_entry)
