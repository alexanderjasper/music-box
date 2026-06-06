"""Web UI for the Music Box simulator.

A single-page faceplate that looks like the device we'll build, driving the same
`MusicBox` core as the CLI. The browser renders the panel and plays the buzzer
cues; this server just exposes the core's methods as a small JSON API.

Run:  python -m web.server          (from the software/ directory)
Then open the printed URL (default http://0.0.0.0:8080).
"""

import json
import os
import sys

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox.config import load_card_map  # noqa: E402
from musicbox.core import MusicBox  # noqa: E402
from musicbox.feedback import CUES, Buzzer  # noqa: E402


class WebBuzzer(Buzzer):
    """Records cues fired during one request so the browser can play them."""

    def __init__(self):
        self.cues = []

    def _emit(self, cue):
        self.cues.append(cue)


app = Flask(__name__)
buzzer = WebBuzzer()
box = MusicBox(card_map=load_card_map(), buzzer=buzzer)

CONNECTED = False
CONNECT_ERROR = None
try:
    box.discover()
    CONNECTED = True
except RuntimeError as e:
    CONNECT_ERROR = str(e)


# Maps an action name from the browser to a core call. Each returns a result dict.
ACTIONS = {
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


@app.get("/")
def index():
    return render_template(
        "index.html",
        cues=json.dumps(CUES),
        connected=CONNECTED,
        connect_error=CONNECT_ERROR or "",
    )


@app.get("/api/state")
def state():
    return jsonify({"connected": CONNECTED, "error": CONNECT_ERROR, **box.state()})


@app.post("/api/action")
def action():
    data = request.get_json(force=True)
    name = data.get("action")
    handler = ACTIONS.get(name)
    if not handler:
        return jsonify({"ok": False, "message": f"unknown action {name!r}"}), 400
    buzzer.cues.clear()
    result = handler(data.get("args", {}))
    # Return the result, the cues that fired, and a fresh state snapshot.
    return jsonify({**result, "cues": list(buzzer.cues), "state": box.state()})


def main():
    port = int(os.environ.get("MUSICBOX_PORT", "8080"))
    if CONNECTED:
        print(f"Connected to: {', '.join(box.rooms())}")
    else:
        print(f"NOT connected to Sonos: {CONNECT_ERROR}\n(UI still loads.)")
    print(f"Open http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
