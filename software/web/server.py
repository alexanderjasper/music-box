"""The Music Box config app — what the box serves at musicbox.local.

  /          the configuration app:
               • map each hardware room-slot → a Sonos room
               • map NFC tags → Sonos Favorites or playlists (live enrollment)
  /labels    lay album art onto a sheet of die-cut card labels, ready to print

`create_app(box, ...)` is an app factory so the same routes serve both a laptop
(this module's module-level `app`, used by `python -m web.server`) and the
on-device service (musicbox/service.py), which passes the *same* box + shared room
map the GPIO panel is using.

Run it on a laptop:  python -m web.server       (from the software/ directory)
"""

import json
import os
import sys

from flask import Flask, Response, jsonify, render_template, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox.config import (  # noqa: E402
    load_card_map,
    load_room_map,
    save_card_map,
    save_room_map,
)
from musicbox.core import MusicBox  # noqa: E402
from musicbox.feedback import ConsoleBuzzer  # noqa: E402
from musicbox.hardware.profile import load_profile  # noqa: E402
from web import labelsheet  # noqa: E402


def create_app(box, *, profile=None, room_map=None, card_path=None, room_path=None,
               nfc_last=None, connected=True, connect_error=None):
    """Build the Flask app over a given MusicBox.

    room_map is a *live* dict shared with the caller (the GPIO panel on the Pi),
    so saving a new mapping here takes effect immediately for the hardware too.
    """
    app = Flask(__name__)
    room_map = room_map if room_map is not None else {}
    slot_ids = list(profile.slot_ids) if profile else []

    def favorites_list(refresh=False):
        try:
            return box.favorite_titles(refresh=refresh)
        except Exception:
            return []

    def playlists_list(refresh=False):
        try:
            return box.playlist_titles(refresh=refresh)
        except Exception:
            return []

    @app.get("/")
    @app.get("/config")
    def config_page():
        return render_template("config.html")

    # --- configuration API --------------------------------------------------

    @app.get("/api/config")
    def get_config():
        # The config page is opened rarely and is exactly where a favorite added
        # in the Sonos app needs to show up, so re-read the list every time. It
        # also freshens the shared cache the playback path matches against.
        return jsonify({
            "sonos_rooms": box.rooms(),
            "slots": slot_ids,
            "room_map": dict(room_map),
            "cards": dict(box.card_map),
            "favorites": favorites_list(refresh=True),
            "playlists": playlists_list(refresh=True),
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

    # --- card labels --------------------------------------------------------

    @app.get("/labels")
    def labels_page():
        return render_template("labels.html")

    @app.get("/api/labels/art")
    def label_art():
        """Proxy the Sonos artwork for one favorite, so the page can show it."""
        title = request.args.get("title", "")
        try:
            data = box.artwork_for(title)
        except Exception as e:
            return jsonify({"ok": False, "message": str(e)}), 502
        if not data:
            return jsonify({"ok": False, "message": "no artwork for that one"}), 404
        side = labelsheet.source_size(data)
        return Response(data, mimetype="image/jpeg",
                        headers={"X-Source-Px": str(side)})

    @app.post("/api/labels/pdf")
    def label_pdf():
        """Build the sheet. Each slot carries either a favorite title or a file."""
        images, soft = {}, []
        for slot in range(1, labelsheet.SLOTS + 1):
            upload = request.files.get(f"file{slot}")
            title = (request.form.get(f"title{slot}") or "").strip()
            if upload and upload.filename:
                data = upload.read()
            elif title:
                try:
                    data = box.artwork_for(title)
                except Exception:
                    data = None
                if not data:
                    return jsonify({"ok": False,
                                    "message": f"No artwork found for {title!r}. "
                                               f"Add an image for that label."}), 400
            else:
                continue
            if labelsheet.source_size(data) < labelsheet.MIN_PX:
                soft.append(slot)
            images[slot] = data

        calib = request.form.get("calib") == "1"
        if not images and not calib:
            return jsonify({"ok": False, "message": "Nothing chosen yet."}), 400
        bleed = float(request.form.get("bleed", 1.0))
        pdf = labelsheet.build_sheet(images, bleed=bleed, calib=calib)
        name = "labels-calibration.pdf" if calib else "labels.pdf"
        return Response(pdf, mimetype="application/pdf", headers={
            "Content-Disposition": f'inline; filename="{name}"',
            "X-Soft-Slots": ",".join(str(s) for s in soft),
        })

    @app.get("/api/nfc/last")
    def nfc_last_seen():
        return jsonify({"uid": nfc_last() if nfc_last else None})

    return app


def _build_sim_app():
    """The laptop simulator app: a fresh box that discovers Sonos at import."""
    box = MusicBox(card_map=load_card_map(), buzzer=ConsoleBuzzer())
    connected, error = True, None
    try:
        box.discover()
    except RuntimeError as e:
        connected, error = False, str(e)
    return create_app(
        box,
        profile=load_profile(),       # so the /config room-mapping demo has slots
        room_map=load_room_map(),
        connected=connected,
        connect_error=error,
    )


app = _build_sim_app()  # module-level for gunicorn (web.server:app) and `python -m web.server`


def main():
    port = int(os.environ.get("MUSICBOX_PORT", "8080"))
    print(f"Open http://localhost:{port}/  (mapping)  ·  /labels  (card labels)")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
