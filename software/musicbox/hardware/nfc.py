"""NFC reading, abstracted so the panel doesn't care how the UID arrives.

`NfcReader.read_uid()` returns the hex UID of a tag on the spot, or None if the
spot is empty. The real reader is a PN532 over I²C; `NullNfcReader` stands in
when NFC is disabled or absent (e.g. on the laptop).
"""


class NfcReader:
    """Interface: one poll returns the current tag's UID, or None."""

    def read_uid(self):
        raise NotImplementedError

    def healthy(self):
        """Whether the reader still answers. Only a reader that can tell says no."""
        return True

    def reset(self):
        """Bring the reader back to a known state, as a power-up would."""

    def close(self):
        pass


class NullNfcReader(NfcReader):
    """No reader present — the spot always reads empty."""

    def read_uid(self):
        return None


class Pn532Reader(NfcReader):
    """PN532 over I²C via adafruit-circuitpython-pn532.

    Set the PN532 board's interface switches to I²C and wire SDA/SCL to GPIO2/3
    (see hardware/WIRING.md). We only ever read the factory UID — nothing is
    written to the tag.
    """

    def __init__(self, read_timeout=0.2):
        self._read_timeout = read_timeout
        self._i2c = None
        self._pn532 = None
        self.reset()

    def reset(self):
        """Open the bus afresh and wake and configure the chip, as at boot."""
        # All Pi-only; imported lazily so this module loads on a laptop.
        import board
        import busio
        from adafruit_pn532.i2c import PN532_I2C

        self.close()
        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._pn532 = PN532_I2C(self._i2c, debug=False)
        self._pn532.SAM_configuration()

    def healthy(self):
        # Raises once the chip no longer answers; a wedged chip that still
        # answers here is what the panel's periodic re-init is for.
        return self._pn532 is not None and self._pn532.firmware_version is not None

    def close(self):
        self._pn532 = None
        if self._i2c is not None:
            try:
                self._i2c.deinit()
            except Exception:
                pass
            self._i2c = None

    def read_uid(self):
        uid = self._pn532.read_passive_target(timeout=self._read_timeout)
        if uid is None:
            return None
        return "".join(f"{b:02X}" for b in uid)
