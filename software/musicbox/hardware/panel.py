"""Panel — wires real controls to the MusicBox core via the slot→room map.

Design split that keeps this testable on a laptop:

  * The `on_*` methods are **pure logic** — they translate a physical event
    (slot 1's button latched in, the knob turned a detent, a tag appeared) into
    a core call, applying the slot→Sonos-room mapping. No gpiozero involved, so
    tests drive them directly.
  * `bind()` is the only Pi-specific part: it reads the profile and constructs
    exactly the gpiozero Buttons / RotaryEncoders that exist, binding their
    events to the `on_*` methods. It also starts the NFC polling thread.

Control semantics follow the agreed design:
  * Room arm + shuffle/repeat are **latching** — the switch position *is* the
    state, so we sync on press/release (and read initial position at boot).
  * Transport (play/next/previous) is **momentary** — act on press.

The slot→room map is a live dict shared with the web config app: when you remap
a slot in the browser, the panel picks it up on the next button press.
"""

import threading

VOLUME_STEP = 2  # volume change per encoder detent


def _err(message):
    return {"ok": False, "message": message}


class VolumeCoalescer:
    """Collapses a burst of encoder detents into as few Sonos calls as possible.

    Each Sonos volume change is a network round-trip (~100ms+). Spinning the dial
    fires a detent every few milliseconds, so doing one API call per detent makes
    the volume crawl seconds behind the knob — and worse, blocks gpiozero's
    callback thread, which then misses further detents.

    So the detent callback only calls `nudge()`: it adds to a pending per-slot
    delta and returns instantly. A worker thread applies the *net* accumulated
    delta in one call. While that (slow) call is in flight, further detents pile
    into the next delta, so a fast spin becomes a few big steps instead of a long
    queue of laggy single steps — we deliberately skip the intermediate values.
    """

    def __init__(self, apply):
        self._apply = apply              # callable(slot_id, net_delta)
        self._pending = {}               # slot_id -> delta not yet applied
        self._lock = threading.Lock()
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def nudge(self, slot_id, delta):
        with self._lock:
            self._pending[slot_id] = self._pending.get(slot_id, 0) + delta
        self._wake.set()

    def _run(self):
        while not self._stop.is_set():
            self._wake.wait()
            self._wake.clear()
            self._drain()

    def _drain(self):
        while True:
            with self._lock:
                if not self._pending:
                    return
                slot_id = next(iter(self._pending))
                delta = self._pending.pop(slot_id)
            try:
                self._apply(slot_id, delta)
            except Exception:
                pass  # a failed call shouldn't kill the worker

    def stop(self):
        self._stop.set()
        self._wake.set()
        self._thread.join(timeout=1.0)


class Panel:
    def __init__(self, box, profile, room_map, nfc=None, on_change=None):
        self.box = box
        self.profile = profile
        self.room_map = room_map        # shared {slot_id: sonos room}, mutated by the web app
        self.nfc = nfc                  # an NfcReader, or None
        self.on_change = on_change      # optional callback(result) after any action
        self.last_uid = None            # most recent tag UID seen (for web enrollment)
        self._present_uid = None        # UID currently on the spot (for removal detection)
        self._controls = []             # keep gpiozero refs alive (else GC unbinds them)
        self._nfc_thread = None
        self._stop = threading.Event()
        # coalesces fast encoder turns into few Sonos calls; built in bind()
        self._volume = None

    # --- pure event handlers (unit-tested without any gpiozero) -------------

    def _room_for(self, slot_id):
        return self.room_map.get(str(slot_id))

    def on_room_set(self, slot_id, armed):
        """Latching arm button: drive the room to match the switch position."""
        room = self._room_for(slot_id)
        if not room:
            self.box.buzzer.error()
            return _err(f"slot {slot_id} is not mapped to a Sonos room")
        is_armed = room in self.box.armed
        if armed != is_armed:
            return self._do(self.box.toggle_room, room)
        return {"ok": True, "message": f"{room} already {'armed' if armed else 'disarmed'}"}

    def on_volume(self, slot_id, delta):
        room = self._room_for(slot_id)
        if not room:
            return _err(f"slot {slot_id} is not mapped to a Sonos room")
        return self._do(self.box.nudge_volume, room, delta)

    def on_play(self):
        return self._do(self.box.play)

    def on_next(self):
        return self._do(self.box.next)

    def on_previous(self):
        return self._do(self.box.previous)

    def on_mode_set(self, mode, on):
        """Latching shuffle/repeat: drive state to match the switch position."""
        if mode == "shuffle":
            return self._do(self.box.set_shuffle, on)
        if mode == "repeat":
            return self._do(self.box.set_repeat, on)
        return _err(f"unknown mode {mode!r}")

    def on_tag(self, uid):
        self.last_uid = uid
        self._present_uid = uid
        result = self._do(self.box.place_card, uid)
        # Turntable behaviour: dropping a recognized card starts playback at once
        # if a room is armed — no separate play press. With no room armed the card
        # is just recognized (chirp) and waits; play stays available for
        # pause/resume. (place_card already beeped an error for an unknown card.)
        if result.get("ok") and self.box.armed:
            return self._do(self.box.play)
        return result

    def on_tag_removed(self):
        self._present_uid = None
        return self._do(self.box.remove_card)

    def _do(self, fn, *args):
        result = fn(*args)
        if self.on_change:
            try:
                self.on_change(result)
            except Exception:
                pass
        return result

    # --- Pi wiring (gpiozero) ----------------------------------------------

    def bind(self):
        """Build the gpiozero controls the profile declares and wire them up."""
        from gpiozero import Button, RotaryEncoder

        p = self.profile
        # Encoder turns go through the coalescer so a fast spin doesn't queue one
        # slow Sonos call per detent (see VolumeCoalescer).
        self._volume = VolumeCoalescer(self.on_volume)

        transport = {"play": self.on_play, "next": self.on_next, "previous": self.on_previous}
        for name, pin in p.transport.items():
            handler = transport.get(name)
            if handler is None:
                continue
            btn = Button(pin, pull_up=True, bounce_time=0.05)
            btn.when_pressed = handler  # momentary: act on press
            self._controls.append(btn)

        for mode, pin in p.modes.items():
            btn = Button(pin, pull_up=True, bounce_time=0.05)
            btn.when_pressed = lambda m=mode: self.on_mode_set(m, True)    # latched in
            btn.when_released = lambda m=mode: self.on_mode_set(m, False)  # popped out
            if btn.is_pressed:  # honour the switch's position at boot
                self.on_mode_set(mode, True)
            self._controls.append(btn)

        for slot in p.room_slots:
            if slot.has_button:
                btn = Button(slot.button, pull_up=True, bounce_time=0.05)
                btn.when_pressed = lambda s=slot.id: self.on_room_set(s, True)
                btn.when_released = lambda s=slot.id: self.on_room_set(s, False)
                if btn.is_pressed and self._room_for(slot.id):
                    self.on_room_set(slot.id, True)  # restore armed state at boot
                self._controls.append(btn)
            if slot.has_encoder:
                enc = RotaryEncoder(slot.encoder_a, slot.encoder_b, max_steps=0)
                enc.when_rotated_clockwise = lambda s=slot.id: self._volume.nudge(s, VOLUME_STEP)
                enc.when_rotated_counter_clockwise = lambda s=slot.id: self._volume.nudge(s, -VOLUME_STEP)
                self._controls.append(enc)

        if self.nfc is not None:
            self.start_nfc()
        return self

    # --- NFC polling --------------------------------------------------------

    def start_nfc(self):
        self._nfc_thread = threading.Thread(target=self._nfc_loop, daemon=True)
        self._nfc_thread.start()

    def _nfc_loop(self):
        # A tag present reads its UID on each poll; empty reads None. Require a
        # few consecutive empties before declaring "removed" so one missed read
        # (common with cheap readers) doesn't falsely stop playback.
        interval = self.profile.nfc_poll_interval
        remove_after = 3
        misses = 0
        while not self._stop.is_set():
            try:
                uid = self.nfc.read_uid()
            except Exception:
                uid = None
            if uid:
                misses = 0
                if uid != self._present_uid:
                    self.on_tag(uid)
            elif self._present_uid is not None:
                misses += 1
                if misses >= remove_after:
                    misses = 0
                    self.on_tag_removed()
            self._stop.wait(interval)

    def stop(self):
        self._stop.set()
        if self._volume is not None:
            self._volume.stop()
        if self._nfc_thread is not None:
            self._nfc_thread.join(timeout=1.0)
        if self.nfc is not None:
            self.nfc.close()
