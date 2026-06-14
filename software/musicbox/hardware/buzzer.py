"""GpioBuzzer — plays the shared cue vocabulary on a real passive piezo.

This is the Pi implementation of the `Buzzer` interface defined in
musicbox/feedback.py. It plays the *same* CUES patterns the console and web
buzzers use, so the box sounds exactly like the simulator rehearsed.

The KY-006 is a **passive** buzzer, so tones come from PWM — gpiozero's
TonalBuzzer. Cues play on a short-lived background thread (serialised by a lock)
so firing a cue never blocks the GPIO callback that triggered it.
"""

import threading
import time

from ..feedback import CUES, Buzzer


class GpioBuzzer(Buzzer):
    def __init__(self, pin, octaves=2):
        # gpiozero is Pi-only; import lazily so this module loads on a laptop.
        from gpiozero import TonalBuzzer
        from gpiozero.tones import Tone

        self._Tone = Tone
        # Default mid-tone A4 ± 1 octave only reaches 880 Hz; our card chirp is
        # 1568 Hz, so widen to ±2 octaves (~110-1760 Hz) to cover every cue.
        self._buzzer = TonalBuzzer(pin, octaves=octaves)
        self._lock = threading.Lock()

    def _emit(self, cue):
        pattern = CUES.get(cue)
        if not pattern:
            return
        threading.Thread(target=self._play, args=(pattern,), daemon=True).start()

    def _play(self, pattern):
        with self._lock:  # one cue at a time — the buzzer is a single resource
            try:
                for freq, ms in pattern:
                    if freq > 0:
                        try:
                            self._buzzer.play(self._Tone(frequency=freq))
                        except ValueError:
                            pass  # out of the buzzer's range — skip, don't crash
                    else:
                        self._buzzer.stop()
                    time.sleep(ms / 1000)
            finally:
                self._buzzer.stop()
