"""NFC reading, abstracted so the panel doesn't care how the UID arrives.

`NfcReader.read_uid()` returns the hex UID of a tag on the spot, or None if the
spot is empty. The real reader is a PN532 over I²C; `NullNfcReader` stands in
when NFC is disabled or absent (e.g. on the laptop).
"""


class NfcReader:
    """Interface: one poll returns the current tag's UID, or None."""

    def read_uid(self):
        raise NotImplementedError

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
        # All Pi-only; imported lazily so this module loads on a laptop.
        import board
        import busio
        from adafruit_pn532.i2c import PN532_I2C

        self._read_timeout = read_timeout
        i2c = busio.I2C(board.SCL, board.SDA)
        self._pn532 = PN532_I2C(i2c, debug=False)
        self._pn532.SAM_configuration()

    def read_uid(self):
        uid = self._pn532.read_passive_target(timeout=self._read_timeout)
        if uid is None:
            return None
        return "".join(f"{b:02X}" for b in uid)
