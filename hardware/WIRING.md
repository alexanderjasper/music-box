# Wiring guide

Exact pin-to-pin connections for the Music Box on a **Raspberry Pi Zero 2 W**
(standard 40-pin header). This finalises the provisional pin budget in
[`BOM.md`](BOM.md): **5 room slots** (3 speakers today + 2 spare), 2 mode buttons,
3 transport buttons, the PN532 NFC reader, and the piezo — **23 of 26 usable GPIO**.

> **Breadboard first, solder later.** Wire everything on a breadboard and prove it
> (test steps at the bottom) before committing solder. Nothing here needs resistors:
> buttons use the Pi's internal pull-ups, the PN532 has its own I²C pull-ups.

## Safety / ground rules

- **Power off the Pi while wiring.** Plug in only to test.
- **The Pi's GPIO is 3.3 V logic — never feed 5 V into a GPIO pin.** The PN532 runs
  from the **3V3** pin (not 5V). Buttons/encoders only switch to **GND**, so they
  can't over-volt anything.
- The Pi has **8 GND pins** but we need ~16 ground connections. Run a **common ground
  bus** (a breadboard ground rail) from one or two Pi GND pins, and land every
  component ground on that rail.
- Pins **27 (GPIO0)** and **28 (GPIO1)** are reserved for HAT EEPROM ID — leave empty.

---

## Pin map (what connects where)

BCM = the GPIO number you use in software. Pin = the physical position on the 40-pin
header (count along the board; pin 1 is the corner nearest the SD card / marked with a
square pad).

| Function | Connects to | BCM | Header pin |
|----------|-------------|-----|-----------|
| **PN532** VCC | 3V3 | — | **1** |
| **PN532** GND | ground bus | — | (any GND) |
| **PN532** SDA | I²C data | GPIO2 | **3** |
| **PN532** SCL | I²C clock | GPIO3 | **5** |
| **Room 1 (Alrum)** button | → GND | GPIO4 | **7** |
| **Room 2 (Køkken)** button | → GND | GPIO5 | **29** |
| **Room 3 (Grys værelse)** button | → GND | GPIO6 | **31** |
| **Room 4 (spare)** button | → GND | GPIO13 | **33** |
| **Room 5 (spare)** button | → GND | GPIO19 | **35** |
| **Shuffle** button | → GND | GPIO26 | **37** |
| **Repeat** button | → GND | GPIO7 | **26** |
| **Previous** button | → GND | GPIO10 | **19** |
| **Play / Pause** button | → GND | GPIO9 | **21** |
| **Next** button | → GND | GPIO8 | **24** |
| **Vol 1 (Alrum)** encoder A / B | → GPIO | GPIO17 / GPIO27 | **11 / 13** |
| **Vol 2 (Køkken)** encoder A / B | → GPIO | GPIO22 / GPIO23 | **15 / 16** |
| **Vol 3 (Grys)** encoder A / B | → GPIO | GPIO24 / GPIO25 | **18 / 22** |
| **Vol 4 (spare)** encoder A / B | → GPIO | GPIO12 / GPIO16 | **32 / 36** |
| **Vol 5 (spare)** encoder A / B | → GPIO | GPIO20 / GPIO21 | **38 / 40** |
| **Piezo** (+) | PWM | GPIO18 | **12** |
| **Piezo** (−) | ground bus | — | (any GND) |

Every encoder's **common (C)** pin → ground bus. Each button's **second terminal** →
ground bus. That's the whole pattern: signal pin to its GPIO, the other side to ground.

---

## Header layout (annotated)

```
                    3V3  (1) ● ● (2)  5V
        PN532 SDA  GPIO2  (3) ● ● (4)  5V
        PN532 SCL  GPIO3  (5) ● ● (6)  GND ── ground bus
      Room1 btn    GPIO4  (7) ● ● (8)  GPIO14   ·free·
                    GND   (9) ● ● (10) GPIO15   ·free·
      Vol1 A      GPIO17 (11) ● ● (12) GPIO18 ── Piezo (+)
      Vol1 B      GPIO27 (13) ● ● (14) GND ──── ground bus
      Vol2 A      GPIO22 (15) ● ● (16) GPIO23 ── Vol2 B
                    3V3  (17) ● ● (18) GPIO24 ── Vol3 A
      Prev btn    GPIO10 (19) ● ● (20) GND ──── ground bus
      Play btn     GPIO9 (21) ● ● (22) GPIO25 ── Vol3 B
      ·free·      GPIO11 (23) ● ● (24) GPIO8 ─── Next btn
                    GND  (25) ● ● (26) GPIO7 ─── Repeat btn
   ·reserved·      GPIO0 (27) ● ● (28) GPIO1    ·reserved·
      Room2 btn    GPIO5 (29) ● ● (30) GND ──── ground bus
      Room3 btn    GPIO6 (31) ● ● (32) GPIO12 ── Vol4 A
      Room4 btn   GPIO13 (33) ● ● (34) GND ──── ground bus
      Room5 btn   GPIO19 (35) ● ● (36) GPIO16 ── Vol4 B
      Shuffle btn GPIO26 (37) ● ● (38) GPIO20 ── Vol5 A
                    GND  (39) ● ● (40) GPIO21 ── Vol5 B
```

---

## Per-component wiring

### PN532 NFC reader (I²C)
Most PN532 V3 boards have a **DIP switch or solder jumpers to pick the interface** —
set it to **I²C** (often "1=OFF, 2=ON"; check your board's silkscreen).

| PN532 pad | → Pi |
|-----------|------|
| VCC | 3V3 (pin 1) |
| GND | ground bus |
| SDA | GPIO2 / pin 3 |
| SCL | GPIO3 / pin 5 |

The board carries its own I²C pull-ups, so no resistors. Enable I²C with
`sudo raspi-config` → Interface Options → I²C.

### Buttons (5 room latching + 2 mode latching + 3 transport momentary)
All ten wire the **same way** — they're just switches:

```
   GPIO pin  ─────[ button ]─────  ground bus
```

One terminal to the listed GPIO, the other to ground. In software each pin uses an
**internal pull-up** (`pull_up=True`), so an open switch reads **HIGH (1)** and a
closed/latched-in switch reads **LOW (0)** — i.e. *active-low*.

- **Latching** room/mode buttons stay mechanically closed when "in", so their pin sits
  LOW for as long as the room is armed / mode is active — the Pi can read armed state
  directly, even right after boot.
- **Momentary** transport buttons read LOW only while held.

### Rotary encoders ×5 (EC11)
An EC11 has **two sides**: the rotary side (pins **A, C, B**) and an optional push-switch
side (2 pins). **We use only the rotary side**; leave the push-switch pins unconnected.

```
   A ── GPIO (listed "A")
   C ── ground bus            (common)
   B ── GPIO (listed "B")
```

Software enables internal pull-ups on A and B and watches their phase to tell
clockwise from counter-clockwise (relative steps → SoCo per-room volume). If you see
jitter on the breadboard, a small **0.1 µF cap from A→GND and B→GND** debounces it
(optional; try without first).

### Piezo buzzer (passive)
```
   GPIO18 (pin 12) ──[ piezo ]── ground bus
```
A small **passive** piezo can be driven straight off GPIO18 (hardware PWM → tones). If
it's too quiet, drive it through an NPN transistor (e.g. 2N2222: GPIO→1 kΩ→base,
emitter→GND, collector→piezo→3V3) — not needed for v1.

---

## Suggested wiring order (breadboard)

1. **Ground bus + PN532 only.** Power on, `i2cdetect -y 1` should show the PN532
   (commonly at address `0x24`). Tap a tag and confirm a UID read with a test script.
2. **One button** (say Play/Pause, GPIO9). Confirm it reads LOW when pressed.
3. **One encoder** (Vol 1, GPIO17/27). Confirm turning it steps a counter up/down.
4. **Piezo** (GPIO18). Confirm a PWM tone plays.
5. Once each *type* works, replicate for the remaining buttons/encoders — same pattern,
   different pins from the table.

### Quick test snippets

```bash
# PN532 present on I²C?
sudo apt install -y i2c-tools
i2cdetect -y 1

# Button on GPIO9 + encoder on GPIO17/27 (uses gpiozero, preinstalled on Pi OS)
python3 - <<'PY'
from gpiozero import Button, RotaryEncoder
from signal import pause
play = Button(9)                       # active-low via internal pull-up
vol1 = RotaryEncoder(17, 27, max_steps=0)
play.when_pressed  = lambda: print("PLAY pressed")
vol1.when_rotated  = lambda: print("vol1 =", vol1.steps)
print("Press play / turn the encoder…")
pause()
PY
```

When all five families check out on the breadboard, transfer to soldered wiring (or a
Pi Zero proto/HAT board) for the enclosure build.

---

## Cross-references

- Parts & quantities: [`BOM.md`](BOM.md)
- Control behaviour (what each button does): the **Control scheme** section in the
  top-level [`README.md`](../README.md)
- The pin numbers above match the **GPIO budget** table in `BOM.md`; if you change one,
  change both.
