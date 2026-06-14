"""Tests for the hardware Panel's pure event logic and the profile loader.

No gpiozero and no Sonos: we stub `soco`, build a real MusicBox over fake
speakers (same fakes as test_core), and call the Panel's `on_*` handlers
directly — exactly what `bind()` would call from a real button/encoder/tag.
The point is to prove the slot→Sonos-room translation, not gpiozero itself.

Run:  python tests/test_panel.py
"""

import os
import sys
import tempfile
import types

# --- stub soco so importing the core works without it ----------------------
_soco = types.ModuleType("soco")
_exc = types.ModuleType("soco.exceptions")
_exc.SoCoException = type("SoCoException", (Exception,), {})
_soco.exceptions = _exc
_soco.discover = lambda timeout=None: set()
sys.modules.setdefault("soco", _soco)
sys.modules.setdefault("soco.exceptions", _exc)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox.core import MusicBox  # noqa: E402
from musicbox.feedback import Buzzer  # noqa: E402
from musicbox.hardware.panel import VOLUME_STEP, Panel  # noqa: E402
from musicbox.hardware.profile import HardwareProfile, RoomSlot, _from_dict, load_profile  # noqa: E402


class FakeFavorite:
    def __init__(self, title):
        self.title = title
        self.resources = [types.SimpleNamespace(uri=f"uri:{title}")]
        self.resource_meta_data = f"meta:{title}"


class FakeLibrary:
    def __init__(self, favorites):
        self._favs = favorites

    def get_sonos_favorites(self):
        return self._favs


class FakeSpeaker:
    def __init__(self, name, favorites):
        self.player_name = name
        self.volume = 30
        self.play_mode = "NORMAL"
        self.music_library = FakeLibrary(favorites)
        self.transport_state = "STOPPED"
        self.log = []

    def join(self, master):
        self.log.append(f"join:{master.player_name}")

    def unjoin(self):
        self.log.append("unjoin")

    def play_uri(self, uri, meta=None):
        self.log.append(f"play_uri:{uri}")
        self.transport_state = "PLAYING"

    def play(self):
        self.transport_state = "PLAYING"

    def pause(self):
        self.transport_state = "PAUSED_PLAYBACK"

    def stop(self):
        self.transport_state = "STOPPED"
        self.log.append("stop")

    def get_current_transport_info(self):
        return {"current_transport_state": self.transport_state}


class RecordingBuzzer(Buzzer):
    def __init__(self):
        self.cues = []

    def _emit(self, cue):
        self.cues.append(cue)


def make_panel(room_map):
    favs = [FakeFavorite("Bohemian Rhapsody"), FakeFavorite("Under Stjernerne")]
    box = MusicBox(card_map={"04AABB": "Bohemian Rhapsody"}, buzzer=RecordingBuzzer())
    box.speakers = {n: FakeSpeaker(n, favs) for n in ("Alrum", "Køkken", "Grys værelse")}
    profile = HardwareProfile(room_slots=[RoomSlot(id="1", button=4, encoder_a=17, encoder_b=27)])
    panel = Panel(box, profile, room_map)
    return panel, box


def check(label, cond):
    if not cond:
        raise AssertionError(f"FAILED: {label}")
    print(f"  ok: {label}")


def main():
    # --- profile loader ----------------------------------------------------
    prof = _from_dict({
        "buzzer": {"pin": 18},
        "nfc": {"enabled": True, "poll_interval": 0.5},
        "transport": {"play": 9, "next": 8},
        "room_slots": [{"id": 1, "button": 4, "encoder_a": 17, "encoder_b": 27},
                       {"id": "2", "encoder_a": 22, "encoder_b": 23}],
    })
    check("buzzer pin parsed", prof.buzzer_pin == 18)
    check("nfc enabled + interval parsed", prof.nfc_enabled and prof.nfc_poll_interval == 0.5)
    check("transport parsed", prof.transport == {"play": 9, "next": 8})
    check("slot ids are strings", prof.slot_ids == ["1", "2"])
    check("slot 1 has button + encoder", prof.slot("1").has_button and prof.slot("1").has_encoder)
    check("slot 2 has encoder but no button", prof.slot("2").has_encoder and not prof.slot("2").has_button)

    with tempfile.TemporaryDirectory() as d:
        check("missing hardware path -> empty profile", load_profile(os.path.join(d, "nope.json")).room_slots == [])

    # --- slot -> room translation -----------------------------------------
    panel, box = make_panel({"1": "Køkken"})

    # latching arm button: pressing-in arms the *mapped* Sonos room
    panel.on_room_set("1", True)
    check("slot 1 armed -> Køkken armed", "Køkken" in box.armed)
    panel.on_room_set("1", True)  # idempotent: already armed, no toggle back
    check("re-arming is idempotent", "Køkken" in box.armed)
    panel.on_room_set("1", False)
    check("releasing disarms Køkken", "Køkken" not in box.armed)

    # encoder detent -> relative volume on the mapped room
    start = box.speakers["Køkken"].volume
    panel.on_volume("1", VOLUME_STEP)
    check("CW detent raises Køkken volume", box.speakers["Køkken"].volume == start + VOLUME_STEP)
    panel.on_volume("1", -VOLUME_STEP)
    check("CCW detent lowers it back", box.speakers["Køkken"].volume == start)

    # unmapped slot -> error + error cue, core untouched
    before = set(box.armed)
    r = panel.on_room_set("9", True)
    check("unmapped slot rejected", not r["ok"])
    check("unmapped slot beeps error", box.buzzer.cues[-1] == "error")
    check("unmapped slot changes nothing", set(box.armed) == before)

    # tag present -> place_card(uid); the uid is remembered for web enrollment
    panel.on_room_set("1", True)
    r = panel.on_tag("04AABB")
    check("tag places the mapped card", box.current_card == "04AABB")
    check("last_uid recorded for enrollment", panel.last_uid == "04AABB")

    # turntable: dropping the card with a room armed auto-plays (no play press)
    check("placing a card auto-plays when armed", box.playing is True)
    check("Køkken got play_uri", any("play_uri" in e for e in box.speakers["Køkken"].log))

    # tag removed -> stops
    panel.on_tag_removed()
    check("removing tag stops playback", box.playing is False)

    # placing a card with NO room armed just recognizes it — no play, no error
    p2, b2 = make_panel({"1": "Køkken"})
    p2.on_tag("04AABB")
    check("unarmed: card is recognized", b2.current_card == "04AABB")
    check("unarmed: nothing plays", b2.playing is False)
    check("unarmed: chirps (not an error)", b2.buzzer.cues[-1] == "card")

    # remapping the live dict reroutes the same slot with no rebuild
    panel.room_map["1"] = "Alrum"
    panel.on_room_set("1", True)
    check("remapped slot now arms Alrum", "Alrum" in box.armed)

    print("\nAll panel checks passed.")


if __name__ == "__main__":
    main()
