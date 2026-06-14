"""The hardware profile: which physical controls exist and on which GPIO pins.

Loaded from `hardware.json` (hand-edited as you wire — *not* the web app). The
shape is intentionally loose so the box can grow incrementally:

    {
      "buzzer":      {"pin": 18},
      "nfc":         {"enabled": true, "poll_interval": 0.3},
      "transport":   {"play": 9, "next": 8, "previous": 10},
      "modes":       {"shuffle": 26, "repeat": 7},
      "room_slots":  [{"id": "1", "button": 4, "encoder_a": 17, "encoder_b": 27}]
    }

Omit a whole section to disable it. Within a room slot, the button and the
encoder are independent — a slot may have just a knob, just a button, or both.
Pins are BCM numbers and follow hardware/WIRING.md.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # software/


@dataclass
class RoomSlot:
    """One physical room position: a latching arm button and/or a volume encoder."""

    id: str
    button: int | None = None
    encoder_a: int | None = None
    encoder_b: int | None = None

    @property
    def has_button(self) -> bool:
        return self.button is not None

    @property
    def has_encoder(self) -> bool:
        return self.encoder_a is not None and self.encoder_b is not None


@dataclass
class HardwareProfile:
    buzzer_pin: int | None = None
    nfc_enabled: bool = False
    nfc_poll_interval: float = 0.3
    transport: dict = field(default_factory=dict)  # {"play": 9, "next": 8, "previous": 10}
    modes: dict = field(default_factory=dict)       # {"shuffle": 26, "repeat": 7}
    room_slots: list = field(default_factory=list)  # [RoomSlot, ...]

    @property
    def slot_ids(self) -> list:
        return [s.id for s in self.room_slots]

    def slot(self, slot_id) -> RoomSlot | None:
        sid = str(slot_id)
        return next((s for s in self.room_slots if s.id == sid), None)


def _from_dict(raw: dict) -> HardwareProfile:
    buzzer = raw.get("buzzer") or {}
    nfc = raw.get("nfc") or {}
    slots = [
        RoomSlot(
            id=str(s["id"]),
            button=s.get("button"),
            encoder_a=s.get("encoder_a"),
            encoder_b=s.get("encoder_b"),
        )
        for s in raw.get("room_slots", [])
    ]
    return HardwareProfile(
        buzzer_pin=buzzer.get("pin"),
        nfc_enabled=bool(nfc.get("enabled", False)),
        nfc_poll_interval=float(nfc.get("poll_interval", 0.3)),
        transport=dict(raw.get("transport") or {}),
        modes=dict(raw.get("modes") or {}),
        room_slots=slots,
    )


def load_profile(path=None) -> HardwareProfile:
    """Load hardware.json. Default location falls back to hardware.example.json;
    an explicit missing path yields an empty profile (nothing enabled)."""
    if path:
        if not os.path.exists(path):
            return HardwareProfile()
        p = path
    else:
        p = os.path.join(HERE, "hardware.json")
        if not os.path.exists(p):
            ex = os.path.join(HERE, "hardware.example.json")
            if not os.path.exists(ex):
                return HardwareProfile()
            p = ex
    with open(p, encoding="utf-8") as f:
        raw = json.load(f)
    return _from_dict(raw)
