"""Endpoint tests for the web app via Flask's test client.

Stubs soco, builds a MusicBox over fake speakers, and exercises the config API
(rooms + cards + nfc) plus the existing action/state routes — no real Sonos, no
running server. Requires Flask (it's in requirements.txt / the dev venv).

Run:  python tests/test_web.py
"""

import os
import sys
import tempfile
import types

_soco = types.ModuleType("soco")
_exc = types.ModuleType("soco.exceptions")
_exc.SoCoException = type("SoCoException", (Exception,), {})
_soco.exceptions = _exc
_soco.discover = lambda timeout=None: set()
sys.modules.setdefault("soco", _soco)
sys.modules.setdefault("soco.exceptions", _exc)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox.core import MusicBox  # noqa: E402
from musicbox.hardware.profile import _from_dict  # noqa: E402
from web.server import WebBuzzer, create_app  # noqa: E402


class FakeFavorite:
    def __init__(self, title):
        self.title = title


class FakeLibrary:
    def __init__(self, favs):
        self._favs = favs

    def get_sonos_favorites(self):
        return self._favs


class FakeSpeaker:
    def __init__(self, name, favs):
        self.player_name = name
        self.volume = 30
        self.music_library = FakeLibrary(favs)


def check(label, cond):
    if not cond:
        raise AssertionError(f"FAILED: {label}")
    print(f"  ok: {label}")


def main():
    with tempfile.TemporaryDirectory() as d:
        cards = os.path.join(d, "cards.json")
        rooms = os.path.join(d, "rooms.json")

        favs = [FakeFavorite("Bohemian Rhapsody"), FakeFavorite("Under Stjernerne")]
        box = MusicBox(card_map={}, buzzer=WebBuzzer())
        box.speakers = {n: FakeSpeaker(n, favs) for n in ("Alrum", "Køkken")}
        room_map = {}
        profile = _from_dict({"room_slots": [{"id": "1"}, {"id": "2"}]})

        app = create_app(box, profile=profile, room_map=room_map,
                         card_path=cards, room_path=rooms,
                         nfc_last=lambda: "04DEADBE", web_buzzer=box.buzzer)
        c = app.test_client()

        # pages render
        check("/ renders", c.get("/").status_code == 200)
        check("/config renders", c.get("/config").status_code == 200)

        # config snapshot
        cfg = c.get("/api/config").get_json()
        check("config lists Sonos rooms", cfg["sonos_rooms"] == ["Alrum", "Køkken"])
        check("config lists hardware slots", cfg["slots"] == ["1", "2"])
        check("config lists live favorites", "Bohemian Rhapsody" in cfg["favorites"])
        check("config exposes last nfc uid", cfg["nfc_last"] == "04DEADBE")

        # save room mapping (valid)
        r = c.post("/api/rooms", json={"room_map": {"1": "Køkken", "2": ""}}).get_json()
        check("valid room map saves", r["ok"] and r["room_map"] == {"1": "Køkken"})
        check("shared room_map dict mutated in place", room_map == {"1": "Køkken"})
        check("rooms.json written", os.path.exists(rooms))

        # reject an unknown room
        bad = c.post("/api/rooms", json={"room_map": {"1": "Nope"}})
        check("unknown room rejected (400)", bad.status_code == 400 and not bad.get_json()["ok"])

        # bind + delete a card
        r = c.post("/api/cards", json={"id": "04AABB", "favorite": "Bohemian Rhapsody"}).get_json()
        check("card binds", r["ok"] and r["cards"]["04AABB"] == "Bohemian Rhapsody")
        check("running box sees the new card", box.card_map.get("04AABB") == "Bohemian Rhapsody")
        check("missing favorite rejected", not c.post("/api/cards", json={"id": "x"}).get_json()["ok"])
        r = c.post("/api/cards", json={"action": "delete", "id": "04AABB"}).get_json()
        check("card deletes", r["ok"] and "04AABB" not in r["cards"])

        # action route still works + captures cues for the browser
        r = c.post("/api/action", json={"action": "play"}).get_json()
        check("play with no room is rejected", not r["ok"])
        check("rejected play returns the error cue", r["cues"] == ["error"])

        # nfc last-seen endpoint
        check("/api/nfc/last returns uid", c.get("/api/nfc/last").get_json()["uid"] == "04DEADBE")

    print("\nAll web checks passed.")


if __name__ == "__main__":
    main()
