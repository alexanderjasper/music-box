"""The on-device service: the physical panel and the config web app, together.

This is what runs on the Pi (`python -m musicbox.service`). It builds one shared
`MusicBox`, wires the GPIO `Panel` to it, and serves the `musicbox.local` web app
over the *same* box and slot→room map — so remapping a room or binding a card in
the browser takes effect on the hardware immediately, and a card read by the
PN532 shows up in the enrollment page.

It degrades gracefully: if a hardware library or pin isn't available (e.g. you
run it on a laptop), that piece is skipped with a note and the rest still runs —
handy for poking at the web app off-device.

It also looks after itself, because it runs for days: a background thread keeps
the speaker list fresh (and keeps looking if Sonos wasn't there at boot), and
pats systemd's watchdog only while the NFC loop is still going round — so a
wedged process is restarted instead of ignoring cards until someone pulls the
plug.
"""

import os
import socket
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox.config import load_card_map, load_room_map  # noqa: E402
from musicbox.core import MusicBox  # noqa: E402
from musicbox.feedback import ConsoleBuzzer  # noqa: E402
from musicbox.hardware.panel import Panel  # noqa: E402
from musicbox.hardware.profile import load_profile  # noqa: E402
from web.server import create_app  # noqa: E402


def _build_buzzer(profile):
    if profile.buzzer_pin is None:
        return ConsoleBuzzer()
    try:
        from musicbox.hardware.buzzer import GpioBuzzer

        return GpioBuzzer(profile.buzzer_pin)
    except Exception as e:  # gpiozero missing / not on a Pi
        print(f"  buzzer: GPIO unavailable ({e}); using console buzzer")
        return ConsoleBuzzer()


def _build_nfc(profile):
    if not profile.nfc_enabled:
        return None
    try:
        from musicbox.hardware.nfc import Pn532Reader

        return Pn532Reader()
    except Exception as e:  # adafruit/i2c missing or no reader attached
        print(f"  nfc: PN532 unavailable ({e}); NFC reading disabled")
        return None


# Sonos calls wait this long for an answer (SoCo's default is 20 s). A speaker
# that moved address otherwise holds a card's reaction for that long before the
# box gets to look for it again.
SONOS_TIMEOUT = 6.0
REFRESH_EVERY = 600.0   # s between re-finding the speakers
WATCHDOG_EVERY = 15.0   # s between pats; musicbox.service allows WatchdogSec=120


def _sd_notify(message):
    """Tell systemd something (sd_notify(3) without the dependency)."""
    addr = os.environ.get("NOTIFY_SOCKET")
    if not addr:
        return  # not under systemd, or no watchdog asked for
    if addr.startswith("@"):
        addr = "\0" + addr[1:]  # an abstract socket
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
            s.connect(addr)
            s.sendall(message.encode())
    except OSError as e:
        print(f"  watchdog: could not notify systemd ({e})")


def _upkeep(box, panel):
    """Forever: pat the watchdog while the panel is alive, refresh the speakers."""
    last_refresh = time.monotonic()
    while True:
        if panel.alive():
            _sd_notify("WATCHDOG=1")
        else:
            print("  watchdog: the NFC loop has stalled; letting systemd restart us")
        due = time.monotonic() - last_refresh >= REFRESH_EVERY
        if not box.speakers or due:
            before = set(box.rooms())
            if box.refresh_speakers():
                if set(box.rooms()) != before:
                    print(f"  speakers: {', '.join(box.rooms())}")
            last_refresh = time.monotonic()
        time.sleep(WATCHDOG_EVERY)


def _log(result):
    mark = "ok" if result.get("ok") else "!!"
    print(f"  [{mark}] {result.get('message', '')}")


def build(discover=True):
    """Assemble box + panel + web app. Returns (app, panel, box)."""
    try:
        import soco.config

        soco.config.REQUEST_TIMEOUT = SONOS_TIMEOUT
    except ImportError:
        pass
    profile = load_profile()
    room_map = load_room_map()  # shared live dict: panel and web both use it
    box = MusicBox(card_map=load_card_map(), buzzer=_build_buzzer(profile))

    connected, error = False, None
    if discover:
        print("Discovering Sonos speakers…")
        try:
            box.discover()
            connected = True
            print(f"  found: {', '.join(box.rooms())}")
        except RuntimeError as e:
            error = str(e)
            print(f"  not connected: {error}")

    panel = Panel(box, profile, room_map, nfc=_build_nfc(profile), on_change=_log)
    try:
        panel.bind()
        controls = len(panel._controls)
        print(f"  panel: {controls} control(s) bound; "
              f"slots={profile.slot_ids or '[]'}; nfc={'on' if panel.nfc else 'off'}")
    except Exception as e:  # gpiozero missing / not on a Pi
        print(f"  panel: GPIO unavailable ({e}); serving web only (no physical controls)")

    app = create_app(
        box,
        profile=profile,
        room_map=room_map,
        nfc_last=lambda: panel.last_uid,
        connected=connected,
        connect_error=error,
    )
    return app, panel, box


def main():
    app, panel, box = build()
    threading.Thread(target=_upkeep, args=(box, panel), daemon=True).start()
    port = int(os.environ.get("MUSICBOX_PORT", "8080"))
    suffix = "" if port == 80 else f":{port}"
    print(f"\nConfig + faceplate at http://musicbox.local{suffix}/  (setup: /config)")
    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    finally:
        panel.stop()


if __name__ == "__main__":
    main()
