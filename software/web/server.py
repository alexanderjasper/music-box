"""Web UI for the Music Box — the simulator faceplate *and* the config app.

Two front-ends, one core:

  /          the faceplate simulator (drag knobs, press buttons) — dev tool
  /config    the configuration app the real box serves at musicbox.local:
               • map each hardware room-slot → a Sonos room
               • map NFC tags → Sonos Favorites (live enrollment on the box)

`create_app(box, ...)` is an app factory so the same routes serve both the
laptop simulator (this module's module-level `app`, used by gunicorn and
`python -m web.server`) and the on-device service (musicbox/service.py), which
passes the *same* box + shared room map the GPIO panel is using.

Run the simulator:  python -m web.server        (from the software/ directory)
"""

import json
import os
import sys

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox.config import (  # noqa: E402
    load_card_map,
    load_room_map,
    save_card_map,
    save_room_map,
)
from musicbox.core import MusicBox  # noqa: E402
from musicbox.feedback import CUES, Buzzer  # noqa: E402
from musicbox.hardware.profile import load_profile  # noqa: E402


class WebBuzzer(Buzzer):
    """Records cues fired during one request so the browser can play them."""

    def __init__(self):
        self.cues = []

    def _emit(self, cue):
        self.cues.append(cue)


def create_app(box, *, profile=None, room_map=None, card_path=None, room_path=None,
               nfc_last=None, web_buzzer=None, connected=True, connect_error=None):
    """Build the Flask app over a given MusicBox.

    room_map is a *live* dict shared with the caller (the GPIO panel on the Pi),
    so saving a new mapping here takes effect immediately for the hardware too.
    web_buzzer (a WebBuzzer) enables cue capture for the browser; omit it on the
    Pi, where the real piezo makes the sound.
    """
    app = Flask(__name__)
    room_map = room_map if room_map is not None else {}
    slot_ids = list(profile.slot_ids) if profile else []

    actions = {
        "toggle_room": lambda a: box.toggle_room(a["room"]),
        "set_volume": lambda a: box.set_volume(a["room"], a["level"]),
        "nudge_volume": lambda a: box.nudge_volume(a["room"], a["delta"]),
        "set_shuffle": lambda a: box.set_shuffle(a["on"]),
        "set_repeat": lambda a: box.set_repeat(a["on"]),
        "place_card": lambda a: box.place_card(a["card"]),
        "remove_card": lambda a: box.remove_card(),
        "play": lambda a: box.play(),
        "next": lambda a: box.next(),
        "previous": lambda a: box.previous(),
    }

    def favorites_list():
        try:
            return box.favorite_titles()
        except Exception:
            return []

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            cues=json.dumps(CUES),
            connected=connected,
            connect_error=connect_error or "",
        )

    @app.get("/config")
    def config_page():
        return render_template("config.html")

    @app.get("/api/state")
    def state():
        return jsonify({"connected": connected, "error": connect_error, **box.state()})

    @app.post("/api/action")
    def action():
        data = request.get_json(force=True)
        name = data.get("action")
        handler = actions.get(name)
        if not handler:
            return jsonify({"ok": False, "message": f"unknown action {name!r}"}), 400
        if web_buzzer is not None:
            web_buzzer.cues.clear()
        result = handler(data.get("args", {}))
        cues = list(web_buzzer.cues) if web_buzzer is not None else []
        return jsonify({**result, "cues": cues, "state": box.state()})

    # --- configuration API --------------------------------------------------

    @app.get("/api/config")
    def get_config():
        return jsonify({
            "sonos_rooms": box.rooms(),
            "slots": slot_ids,
            "room_map": dict(room_map),
            "cards": dict(box.card_map),
            "favorites": favorites_list(),
            "nfc_last": nfc_last() if nfc_last else None,
        })

    @app.post("/api/rooms")
    def save_rooms():
        data = request.get_json(force=True)
        new_map = data.get("room_map", {})
        valid = set(box.rooms())
        cleaned = {}
        for slot, room in new_map.items():
            if not room:
                continue  # blank = leave the slot unassigned
            if valid and room not in valid:
                return jsonify({"ok": False, "message": f"unknown Sonos room {room!r}"}), 400
            cleaned[str(slot)] = room
        room_map.clear()
        room_map.update(cleaned)  # mutate the shared dict in place so the panel sees it
        save_room_map(room_map, room_path)
        return jsonify({"ok": True, "message": "Room mapping saved.", "room_map": dict(room_map)})

    @app.post("/api/cards")
    def save_cards():
        data = request.get_json(force=True)
        cid = str(data.get("id", "")).strip()
        if not cid:
            return jsonify({"ok": False, "message": "Missing card id / tag UID."}), 400
        if data.get("action") == "delete":
            box.card_map.pop(cid, None)
            msg = f"Removed card {cid!r}."
        else:
            fav = str(data.get("favorite", "")).strip()
            if not fav:
                return jsonify({"ok": False, "message": "Pick a favorite to bind."}), 400
            box.card_map[cid] = fav  # the running box sees the new card immediately
            msg = f"Bound {cid!r} → {fav!r}."
        save_card_map(box.card_map, card_path)
        return jsonify({"ok": True, "message": msg, "cards": dict(box.card_map)})

    @app.get("/api/nfc/last")
    def nfc_last_seen():
        return jsonify({"uid": nfc_last() if nfc_last else None})

    return app


def _build_sim_app():
    """The laptop simulator app: a fresh box that discovers Sonos at import."""
    box = MusicBox(card_map=load_card_map(), buzzer=WebBuzzer())
    connected, error = True, None
    try:
        box.discover()
    except RuntimeError as e:
        connected, error = False, str(e)
    return create_app(
        box,
        profile=load_profile(),       # so the /config room-mapping demo has slots
        room_map=load_room_map(),
        web_buzzer=box.buzzer,
        connected=connected,
        connect_error=error,
    )


app = _build_sim_app()  # module-level for gunicorn (web.server:app) and `python -m web.server`


def main():
    port = int(os.environ.get("MUSICBOX_PORT", "8080"))
    print(f"Open http://localhost:{port}  (faceplate)  ·  /config  (mapping)")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
