#!/usr/bin/env python3
"""Music Box — first GPIO bring-up spike (button → buzzer).

The point of this script is to prove the *hardware* end to end on the Pi, the
same way `spike_sonos.py` proved the Sonos end: one button and the passive
piezo, wired on a breadboard, with the simplest possible behaviour —

    hold the button  ->  the buzzer sounds
    release          ->  it stops

If that works, the whole "Pi reads a GPIO input and drives a PWM output" chain
is validated, and every other button/encoder is just more of the same pattern.

WIRING (Pi powered OFF while you wire — see hardware/WIRING.md):

    Momentary button:  GPIO9  (pin 21) ──[ button ]── GND (pin 25)
    KY-006 buzzer:     S → GPIO18 (pin 12)
                       − → GND     (pin 20)      (middle pin unconnected)

The KY-006 is a *passive* buzzer, so it needs a PWM signal to make a tone
(gpiozero's TonalBuzzer does this) — a plain on/off won't make a sound.

SETUP (on the Pi, over SSH):

    # gpiozero + the lgpio backend aren't in Raspberry Pi OS *Lite* by default:
    sudo apt update && sudo apt install -y python3-gpiozero python3-lgpio

USAGE (run with the system Python, where gpiozero lives — not a venv):

    python3 spike_gpio.py                 # button on GPIO9, buzzer on GPIO18
    python3 spike_gpio.py --button 9 --buzzer 18
    python3 spike_gpio.py --self-test     # just chirp the buzzer and exit

On start it plays a short rising chirp so you know the buzzer works even before
you touch the button. Ctrl-C to quit.
"""

import argparse
import sys
from time import sleep

try:
    from gpiozero import Button, TonalBuzzer
    from gpiozero.tones import Tone
    from signal import pause
except ImportError:
    sys.exit(
        "Could not import gpiozero. This script runs on the Raspberry Pi.\n"
        "Install it with:  sudo apt install -y python3-gpiozero python3-lgpio"
    )


def chirp(buzzer):
    """A short rising 'card recognized'-style confirmation chirp."""
    for note in ("A4", "C5", "E5"):
        buzzer.play(Tone(note))
        sleep(0.08)
    buzzer.stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--button", type=int, default=9,
                        help="BCM pin for the momentary button (default: 9)")
    parser.add_argument("--buzzer", type=int, default=18,
                        help="BCM pin for the passive buzzer (default: 18)")
    parser.add_argument("--self-test", action="store_true",
                        help="just chirp the buzzer once and exit (no button needed)")
    args = parser.parse_args()

    buzzer = TonalBuzzer(args.buzzer)

    print(f"Buzzer self-test on GPIO{args.buzzer}…")
    chirp(buzzer)

    if args.self_test:
        print("Self-test done.")
        return

    # Momentary button: active-low via the Pi's internal pull-up (open = HIGH,
    # pressed = pulled to GND = LOW). bounce_time smooths mechanical chatter.
    button = Button(args.button, pull_up=True, bounce_time=0.05)

    button.when_pressed = lambda: buzzer.play(Tone("A4"))
    button.when_released = buzzer.stop

    print(f"Ready: hold the button on GPIO{args.button} to sound the buzzer "
          f"on GPIO{args.buzzer}. Ctrl-C to quit.")
    pause()


if __name__ == "__main__":
    main()
