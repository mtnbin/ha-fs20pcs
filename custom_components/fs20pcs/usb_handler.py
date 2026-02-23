import logging
import hid
import threading

from .const import USB_VENDOR, USB_PRODUCT

_LOGGER = logging.getLogger(__name__) # TODO

class FS20USBHandler:
    """Singleton USB HID handler for FS20 PCS."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FS20USBHandler, cls).__new__(cls)
                cls._instance.device = None
        return cls._instance

    def open(self):
        if self.device is None:
            self.device = hid.device()
            self.device.open(USB_VENDOR, USB_PRODUCT)
            self.device.set_nonblocking(0)

    def close(self):
        if self.device:
            self.device.close()
            self.device = None

    # -------------------------------------------------------------
    # FS20 address conversion
    # -------------------------------------------------------------
    def _map_fs20_value(self, fs20_str):
        """
        Converts readable FS20 notation 1112 → index in table.
        FS20 digits: 1..4, grouped in quads.
        Example: '1213'
        """
        if len(fs20_str) != 4:
            raise ValueError("FS20 code must have exactly 4 digits")

        val = 0
        for i, digit in enumerate(fs20_str):
            d = int(digit)
            if d < 1 or d > 4:
                raise ValueError("FS20 digits must be 1..4")
            val = val * 4 + (d - 1)

        return val

    def convert_housecode(self, housecode_str):
        """Convert '1112 1234' → (HC1, HC2)."""
        parts = housecode_str.replace(" ", "")
        if len(parts) != 8:
            raise ValueError("Housecode must be 8 digits")
        
        hc1 = self._map_fs20_value(parts[0:4])
        hc2 = self._map_fs20_value(parts[4:8])
        return hc1, hc2

    def convert_address(self, address_str):
        """Convert FS20 device address '1213' → FS20 address byte."""
        return self._map_fs20_value(address_str)
    
    # -------------------------------------------------------------
    # Send FS20 command
    # -------------------------------------------------------------
    def send(self, hc1, hc2, adr, cmd, ext=0):
        """
        Sends FS20 command via HID.
        Format: ReportID=1, Size=6, CmdID=F1, HC1,HC2,Adr,Cmd,Ext
        Total 11 bytes.
        """
        _LOGGER.debug(f"USB_handler send HC1: {hc1}, HC2: {hc2}, Adr: {adr}, CMD: {cmd}, Ext: {ext}")
        if self.device is None:
            self.open()

        frame = [
            0x01,   # Report-ID
            0x06,   # Byte count
            0xF1,   # Command ID: Send once
            hc1,
            hc2,
            adr,
            cmd,
            ext,
            0x00,
            0x00,
            0x00
        ]
        self.device.write(bytes(frame))
