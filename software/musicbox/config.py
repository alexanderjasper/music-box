"""Persisted configuration & data for the Music Box.

Two small JSON files hold what the **config web app edits**:

  cards.json    card id (NFC tag UID) -> a Sonos Favorite title to play
  rooms.json    room-slot id          -> a Sonos room (player) name

(The third config file, `hardware.json` — which physical controls exist and on
which GPIO pins — is hand-edited as you wire and is loaded separately by
`musicbox.hardware.profile`, not here. This module is only the web-editable data.)

Because the web app writes these while the box is running, saves are **atomic**:
write a temp file, `fsync`, then `os.replace`. A power cut mid-save can then only
leave the old file or the new one, never a half-written one. That's what lets the
box run from a read-only root filesystem with these two files on a small writable
partition (see the project README, open question #8).

The `card id` stands in for an NFC tag UID on the real device; in the laptop
simulator it's just a human-friendly name. Either way it's only a string key.
"""

import json
import os
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the software/ dir

# Where the two web-editable files live. Defaults to software/, alongside the code,
# which is what sync.sh preserves across deploys. Point MUSICBOX_DATA_DIR at a
# writable mount when the root filesystem goes read-only, or saves land in the RAM
# overlay and vanish on reboot. (hardware.json is hand-edited, never written, so it
# stays with the code either way.)
DATA_DIR = os.environ.get("MUSICBOX_DATA_DIR") or HERE


def _path(name, path):
    return path if path else os.path.join(DATA_DIR, name)


def _atomic_write_json(path, data):
    """Write `data` as pretty JSON to `path` atomically (temp file -> fsync -> rename)."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)  # atomic on POSIX
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _load_map(name, example, path=None):
    """Load the map JSON, dropping _-prefixed keys.

    For the *default* location (path is None) we fall back to the bundled
    `example` file so a fresh checkout has something to show. For an *explicit*
    path (tests, or a real on-Pi data file) a missing file just means "empty" —
    no surprise fallback to the example.
    """
    if path:
        if not os.path.exists(path):
            return {}
        p = path
    else:
        p = os.path.join(DATA_DIR, name)
        if not os.path.exists(p):
            ex = os.path.join(HERE, example)
            if not os.path.exists(ex):
                return {}
            p = ex
    with open(p, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not str(k).startswith("_")}


# --- cards: NFC tag UID -> Sonos Favorite title ------------------------------

def load_card_map(path=None):
    """Load cards.json (falling back to cards.example.json). Ignores _-prefixed keys."""
    return _load_map("cards.json", "cards.example.json", path)


def save_card_map(card_map, path=None):
    """Atomically write the card map to cards.json."""
    data = {"_comment": "card id (NFC tag UID) -> Sonos Favorite title. Edited by the web config UI."}
    data.update({k: v for k, v in card_map.items() if not str(k).startswith("_")})
    _atomic_write_json(_path("cards.json", path), data)


# --- rooms: music-box room-slot id -> Sonos room (player) name ---------------

def load_room_map(path=None):
    """Load rooms.json (falling back to rooms.example.json). Ignores _-prefixed keys."""
    return _load_map("rooms.json", "rooms.example.json", path)


def save_room_map(room_map, path=None):
    """Atomically write the slot->room map to rooms.json."""
    data = {"_comment": "music-box room-slot id -> Sonos room name. Edited by the web config UI."}
    data.update({str(k): v for k, v in room_map.items() if not str(k).startswith("_")})
    _atomic_write_json(_path("rooms.json", path), data)
