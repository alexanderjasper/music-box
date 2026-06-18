"""Audio feedback for a screenless device.

The box has no display, so a piezo buzzer is how it talks back: a chirp when a
card is read, a click when a room is armed, an error buzz when you do something
that can't happen. This module defines the *vocabulary* of cues once, so the
rest of the code calls `buzzer.error()` and never cares how the sound is made.

`ConsoleBuzzer` prints the cue — used on a laptop during development.
On the Pi, a `GpioBuzzer` (see comment at the bottom) will play the same cues as
PWM tones on a GPIO pin. Swapping one for the other changes nothing else.
"""


# Each cue maps to a short tone pattern: a list of (frequency_hz, milliseconds).
# Frequency 0 = silence (a gap). A real GPIO buzzer will play these; the console
# buzzer just names them. Defining them here keeps laptop and Pi behaviour identical.
CUES = {
    "card":    [(1175, 60), (1568, 90)],          # rising chirp — card recognized
    # The arm switches don't latch down, so the *direction* of the sweep is the
    # state readout: a rising ring means "on", a falling ring means "off". Four
    # close steps over ~150 ms read as one glide rather than separate beeps.
    "arm":     [(587, 35), (784, 35), (988, 35), (1319, 55)],   # rising ring — armed
    "disarm":  [(1319, 35), (988, 35), (784, 35), (587, 55)],   # falling ring — disarmed
    "confirm": [(1047, 70)],                       # blip — playback started
    "mode":    [(1319, 30)],                       # tick — shuffle/repeat changed
    "error":   [(220, 180), (0, 60), (220, 180)],  # low double buzz — not allowed
}

# Human-readable labels, only used by the console buzzer.
_LABELS = {
    "card": "card recognized",
    "arm": "room armed (rising ring)",
    "disarm": "room disarmed (falling ring)",
    "confirm": "playback started",
    "mode": "mode changed",
    "error": "error / not allowed",
}


class Buzzer:
    """Semantic cues. Subclasses implement `_emit(cue_name)`."""

    def card_recognized(self):
        self._emit("card")

    def armed(self):
        self._emit("arm")

    def disarmed(self):
        self._emit("disarm")

    def confirm(self):
        self._emit("confirm")

    def mode_changed(self):
        self._emit("mode")

    def error(self):
        self._emit("error")

    def _emit(self, cue):
        raise NotImplementedError


class ConsoleBuzzer(Buzzer):
    """Development buzzer: prints the cue instead of making sound."""

    def _emit(self, cue):
        label = _LABELS.get(cue, cue)
        print(f"    \N{MUSICAL NOTE} buzz: {label}")


class SilentBuzzer(Buzzer):
    """No output — useful for scripted/non-interactive runs."""

    def _emit(self, cue):
        pass


# On the Raspberry Pi, add a GpioBuzzer here, e.g. (sketch):
#
#     import RPi.GPIO as GPIO
#     class GpioBuzzer(Buzzer):
#         def __init__(self, pin):
#             GPIO.setup(pin, GPIO.OUT)
#             self._pwm = GPIO.PWM(pin, 1)
#         def _emit(self, cue):
#             for freq, ms in CUES[cue]:
#                 if freq:
#                     self._pwm.ChangeFrequency(freq); self._pwm.start(50)
#                 else:
#                     self._pwm.stop()
#                 time.sleep(ms / 1000)
#             self._pwm.stop()
#
# Nothing else in the codebase changes — the CLI just constructs a different Buzzer.
