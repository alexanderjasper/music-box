"""Logic tests for MusicBox, using fake speakers so no real Sonos is needed.

Stubs the `soco` module before importing the core, then drives the box through
the exact sequences the panel produces. Run:  python tests/test_core.py
"""

import os
import sys
import types

# --- stub the `soco` package so `import soco` works without it installed ----
_soco = types.ModuleType("soco")
_exc = types.ModuleType("soco.exceptions")


class SoCoException(Exception):
    pass


_exc.SoCoException = SoCoException
_soco.exceptions = _exc
_soco.discover = lambda timeout=None: set()
sys.modules["soco"] = _soco
sys.modules["soco.exceptions"] = _exc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox.core import MusicBox  # noqa: E402
from musicbox.feedback import Buzzer  # noqa: E402


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

    def next(self):
        self.log.append("next")

    def previous(self):
        self.log.append("previous")

    def get_current_transport_info(self):
        return {"current_transport_state": self.transport_state}


class RecordingBuzzer(Buzzer):
    def __init__(self):
        self.cues = []

    def _emit(self, cue):
        self.cues.append(cue)


def make_box():
    favs = [FakeFavorite("Bohemian Rhapsody"), FakeFavorite("Discover Sonos Radio")]
    box = MusicBox(card_map={"bohemian": "Bohemian Rhapsody"}, buzzer=RecordingBuzzer())
    box.speakers = {n: FakeSpeaker(n, favs) for n in ("Alrum", "Køkken", "Grys værelse")}
    return box


def check(label, cond):
    if not cond:
        raise AssertionError(f"FAILED: {label}")
    print(f"  ok: {label}")


def main():
    # play with no room armed -> error beep, no-op
    box = make_box()
    r = box.play()
    check("no-room play is rejected", not r["ok"])
    check("no-room play beeps error", box.buzzer.cues == ["error"])

    # arm by fuzzy name
    box = make_box()
    check("fuzzy arm 'kok' resolves Køkken", box.toggle_room("kok")["ok"])
    check("Køkken is armed", "Køkken" in box.armed)
    check("arm fired arm cue", box.buzzer.cues[-1] == "arm")

    # unknown card -> error, no card on spot
    check("unknown card rejected", not box.place_card("nope")["ok"])
    check("no card on spot after bad card", box.current_card is None)

    # good card -> chirp
    check("known card accepted", box.place_card("bohemian")["ok"])
    check("card chirps", box.buzzer.cues[-1] == "card")

    # play with armed room + card -> plays favorite on coordinator
    r = box.play()
    check("play succeeds", r["ok"])
    check("coordinator is Køkken", box.coordinator_name == "Køkken")
    check("Køkken got play_uri", any("play_uri" in e for e in box.speakers["Køkken"].log))
    check("playing flag set", box.playing is True)

    # arm a second room while playing -> joins live
    box.toggle_room("Alrum")
    check("Alrum joined coordinator live", any("join:Køkken" in e for e in box.speakers["Alrum"].log))

    # volume: absolute and relative, clamped
    check("absolute volume set", box.set_volume("Alrum", 80)["ok"])
    check("Alrum volume is 80", box.speakers["Alrum"].volume == 80)
    box.nudge_volume("Alrum", "+50")
    check("relative volume clamps at 100", box.speakers["Alrum"].volume == 100)

    # shuffle+repeat -> SHUFFLE play_mode applied to coordinator
    box.set_shuffle(True)
    box.set_repeat(True)
    check("play_mode is SHUFFLE", box.speakers["Køkken"].play_mode == "SHUFFLE")

    # next works while playing
    check("next succeeds", box.next()["ok"])
    check("coordinator got next", "next" in box.speakers["Køkken"].log)

    # disarm coordinator's partner stops it live
    box.toggle_room("Alrum")
    check("Alrum unjoined live", "unjoin" in box.speakers["Alrum"].log)

    # play with armed room but no card -> pause/resume toggle
    box2 = make_box()
    box2.toggle_room("Alrum")
    box2.speakers["Alrum"].transport_state = "PLAYING"
    r = box2.play()
    check("no-card play pauses when playing", r["message"] == "Paused")

    print("\nAll core-logic checks passed.")


if __name__ == "__main__":
    main()
