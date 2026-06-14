#!/usr/bin/env python3
"""Music Box — NFC bring-up spike (read a tag UID on the PN532).

The on-Pi companion to spike_gpio.py: the smallest end-to-end proof that the
PN532 reader works over I²C and that software can read a tag's UID — the value
that becomes the key in cards.json and that the /config page captures during
enrollment.

WIRING (PN532 in I²C mode — see hardware/WIRING.md):

    VCC → 3V3 (pin 1)      SDA → GPIO2 (pin 3)
    GND → ground           SCL → GPIO3 (pin 5)

Enable I²C first (`sudo raspi-config nonint do_i2c 0 && sudo reboot`) and confirm
the board shows up: `i2cdetect -y 1` should list it (commonly at 0x24).

SETUP (on the Pi):

    sudo apt install -y python3-pip
    python3 -m pip install --break-system-packages adafruit-circuitpython-pn532 adafruit-blinka

USAGE:

    python3 spike_nfc.py            # prints firmware, then UIDs as you tap tags

If `firmware_version` hangs or errors, it's the PN532 I²C clock-stretching quirk:
add `dtparam=i2c_arm_baudrate=10000` to /boot/firmware/config.txt, reboot, retry.
"""

import argparse
import sys
from time import sleep


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--interval", type=float, default=0.3,
                        help="seconds between polls (default: 0.3)")
    args = parser.parse_args()

    try:
        import board
        import busio
        from adafruit_pn532.i2c import PN532_I2C
    except ImportError:
        sys.exit(
            "Could not import the PN532 libraries. Install them with:\n"
            "  python3 -m pip install --break-system-packages "
            "adafruit-circuitpython-pn532 adafruit-blinka"
        )

    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)

    _ic, ver, rev, _support = pn532.firmware_version  # raises if comms are broken
    print(f"PN532 firmware {ver}.{rev} — reader is talking.")
    pn532.SAM_configuration()

    print("Tap a tag on the spot…  (Ctrl-C to quit)")
    present = None  # the UID currently on the spot, so we only log changes
    try:
        while True:
            uid = pn532.read_passive_target(timeout=0.2)
            if uid is None:
                if present is not None:
                    print("  … tag removed")
                    present = None
            else:
                hexuid = "".join(f"{b:02X}" for b in uid)
                if hexuid != present:
                    print(f"  tag: {hexuid}")
                    present = hexuid
            sleep(args.interval)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
