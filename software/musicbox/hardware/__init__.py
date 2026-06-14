"""The Music Box hardware layer — what makes the real device tick.

The `MusicBox` core (musicbox/core.py) is hardware-agnostic on purpose. This
package is the *third* front-end over it (after the CLI and the web simulator):
real GPIO buttons, rotary encoders, an NFC reader and a piezo buzzer.

Everything is driven by a declarative profile (`hardware.json`, loaded by
`profile.load_profile`): you list which controls exist and on which pins, and
the `Panel` builds *only those* and wires them to the core. Add a part → edit
the JSON → restart. No code change to grow from one room to five.

The heavy, Pi-only dependencies (gpiozero, adafruit PN532) are imported lazily
inside the classes that use them, so this package imports fine on a laptop for
testing the pure event-handling logic.
"""

from .buzzer import GpioBuzzer
from .nfc import NfcReader, NullNfcReader, Pn532Reader
from .panel import Panel
from .profile import HardwareProfile, RoomSlot, load_profile

__all__ = [
    "GpioBuzzer",
    "NfcReader",
    "NullNfcReader",
    "Pn532Reader",
    "Panel",
    "HardwareProfile",
    "RoomSlot",
    "load_profile",
]
