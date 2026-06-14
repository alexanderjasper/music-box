"""Tests for the persistence layer (config.py): atomic save/load of the
card and room maps. No Sonos and no hardware needed.

Run:  python tests/test_config.py
"""

import os
import sys
import tempfile
import types

# Stub `soco` so importing the musicbox package works without it installed
# (config.py itself needs no Sonos — only the package __init__ pulls soco in).
_soco = types.ModuleType("soco")
_exc = types.ModuleType("soco.exceptions")
_exc.SoCoException = type("SoCoException", (Exception,), {})
_soco.exceptions = _exc
_soco.discover = lambda timeout=None: set()
sys.modules.setdefault("soco", _soco)
sys.modules.setdefault("soco.exceptions", _exc)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox import config  # noqa: E402


def check(label, cond):
    if not cond:
        raise AssertionError(f"FAILED: {label}")
    print(f"  ok: {label}")


def main():
    with tempfile.TemporaryDirectory() as d:
        cards = os.path.join(d, "cards.json")
        rooms = os.path.join(d, "rooms.json")

        # Missing file -> empty map (no crash).
        check("missing cards -> {}", config.load_card_map(cards) == {})
        check("missing rooms -> {}", config.load_room_map(rooms) == {})

        # Card map round-trips, including a Danish/diacritic favorite title.
        cmap = {"04A2B3C4": "Bohemian Rhapsody", "04F10293": "Under Stjernerne"}
        config.save_card_map(cmap, cards)
        check("cards round-trip", config.load_card_map(cards) == cmap)

        # Room map round-trips; keys are coerced to strings.
        config.save_room_map({1: "Køkken", "2": "Alrum"}, rooms)
        check("rooms round-trip (str keys)",
              config.load_room_map(rooms) == {"1": "Køkken", "2": "Alrum"})

        # The injected _comment is written but never loaded back as data.
        import json
        with open(cards, encoding="utf-8") as f:
            raw = json.load(f)
        check("_comment is written to disk", "_comment" in raw)
        check("_comment is dropped on load", "_comment" not in config.load_card_map(cards))

        # Saving again overwrites cleanly (no stale keys leak in).
        config.save_card_map({"X": "Discover Sonos Radio"}, cards)
        check("re-save replaces content", config.load_card_map(cards) == {"X": "Discover Sonos Radio"})

        # Atomicity: no leftover temp files in the directory after a save.
        leftovers = [n for n in os.listdir(d) if n.startswith(".tmp-")]
        check("no temp files left behind", leftovers == [])

    print("\nAll config checks passed.")


if __name__ == "__main__":
    main()
