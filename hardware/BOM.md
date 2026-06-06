# Bill of Materials & where to buy (Denmark)

Everything needed to build the Music Box, with Danish/EU sources. You already have
the **3D printer + filament**, so all knobs, button caps and the enclosure are
printed (free). Prices are indicative (DKK, incl. VAT) and will vary — check current
listings. Quantities are for the agreed design: **up to 5 rooms** (3 speakers today + 2
spare slots for future expansion), NFC cards, no display.

> New to soldering? You'll need a basic iron (see "Tools"). Encoders, buttons, the
> buzzer and the NFC module all need a few solder joints. Start on a **breadboard**
> first (no soldering) to prove the wiring, then solder for the final build.

## Core electronics

| # | Part | Qty | ≈ DKK | Notes |
|---|------|-----|------|-------|
| 1 | **Raspberry Pi Zero 2 W** (get the **WH** = pre-soldered header) | 1 | 150–250 | The brain. WH saves you soldering the 40-pin header. |
| 2 | microSD card 16–32 GB (A1) | 1 | 50–80 | Runs Raspberry Pi OS Lite. |
| 3 | 5V micro-USB power supply (≥2.5A) | 1 | 70–110 | Pi Zero uses **micro-USB** for power (not USB-C). Official Pi PSU is reliable. |
| 4 | **PN532 NFC module** (V3, I²C/SPI/UART) | 1 | 80–110 | Reads the cards. We use I²C (2 wires). |
| 5 | **NTAG215 NFC tags/stickers** | 1 pack (50–100) | 120–200 | One per card. Buy in bulk; 25 mm round stickers are easy to embed. |

## Controls (the panel)

| # | Part | Qty | ≈ DKK | Notes |
|---|------|-----|------|-------|
| 6 | **Rotary encoder, EC11** (6 mm knurled shaft) | 5 | 10–25 ea | One volume knob per room slot (3 used + 2 spare). Relative (no analog pin needed). Print the knobs. |
| 7 | **Latching push-button** (push-on/push-off, ~16 mm) | 7 | 15–35 ea | 5 room-arm + shuffle + repeat. The cap **stays pressed in when active** — no LED needed; position *is* the state. Also: holds state across power-off, so the box remembers your selection. |
| 8 | **Momentary push-button** (12–16 mm) | 3 | 10–20 ea | Previous / play-pause / next. (Play gets a printed combined ▶❚❚ cap.) |
| 9 | **Passive piezo buzzer** | 1 | 5–15 | Audio feedback (chirps/error). *Passive* so PWM can play tones — not an active beeper. |

## Wiring & passives

| # | Part | Qty | ≈ DKK | Notes |
|---|------|-----|------|-------|
| 10 | Breadboard (830-point) | 1 | 30–60 | Prototype before soldering. |
| 11 | Jumper wires (M-F, M-M, F-F kit) | 1 | 40–60 | For breadboarding and Pi connections. |
| 12 | Hook-up / silicone wire (thin, ~26 AWG) | 1 | 40 | For the final soldered build. |
| 13 | (Optional) Resistor assortment | 1 kit | 40–60 | Buttons use the Pi's internal pull-ups, so likely none needed for v1. Handy to have. |
| 14 | (Optional) Pi Zero proto/HAT board | 1 | 30–60 | Tidy permanent wiring instead of loose solder. |

## Tools (if you don't have them)

| # | Part | ≈ DKK | Notes |
|---|------|------|-------|
| 15 | Temperature-controlled soldering iron + solder | 200–450 | Kjell & Company has these in-store (walk-in). A basic 60W is fine to learn on. |
| 16 | Wire stripper / side cutters | 60–120 | |
| 17 | (Nice) Multimeter | 80–200 | For checking connections/continuity. |

## 3D printed (you make these — no purchase)

- Enclosure (case + faceplate with holes for buttons, encoders, card spot, buzzer grille).
- 3 knobs (fit EC11 6 mm knurled shaft).
- Button caps — incl. multi-material/multi-colour **shuffle/repeat symbol caps** and the
  **room-name caps** if you print labels rather than apply stickers.
- A card spot/tray and the cards themselves (NTAG215 sticker inside each).

---

## Where to buy (Denmark / EU)

**One-stop-ish, Danish, fast:**
- **[raspberrypi.dk](https://raspberrypi.dk/)** — Pi Zero 2 W (WH), microSD, official PSU, header, case. The obvious place for items 1–3.
- **[let-elektronik.dk](https://let-elektronik.dk/rfid-nfc-tags-sensorer)** — wide hobby range: PN532/NFC, encoders, buttons, buzzer, breadboard, jumpers, LEDs, resistors (items 4, 6–13).
- **[elektronik-lavpris.dk](https://elektronik-lavpris.dk/)** — general hobby electronics, often cheap (PN532, buttons, passives).
- **[bitbyg.dk](https://bitbyg.dk/shop/pn532-nfc-rfid-module-v3/)** / **[ebits.dk](https://ebits.dk/products/pn532-rfid-laeser-inkl-noglekort-og-noglebrik)** — PN532 module (≈ 86 kr).
- **[idekort.dk](https://idekort.dk/vare-kategori/rfid-og-kontaktloese-kort-og-brikker/nfc-ntag-produkter/)** — bulk NTAG213/215/216 tags & cards (item 5).
- **[arduinotech.dk](https://arduinotech.dk/shop/ntag-rfid-nfc-tag-smartphones/)** — NTAG215 tags, Arduino-style modules.
- **Kjell & Company** (kjell.com/dk, **physical stores** in DK) — soldering iron, breadboard, wires, tools (items 10–17) you can pick up today.

**Cheapest (slower shipping):**
- **AliExpress** — PN532, EC11 encoders, push-buttons, NTAG215 (100-packs), jumper kits. Weeks of shipping but lowest cost; great for the bulk tags and the generic encoders/buttons.

**EU, reliable, ships to DK:**
- **[BerryBase.de](https://www.berrybase.de/en/)** — Pi boards, PN532, NTAG215 packs, components.
- **Farnell/[dk.farnell.com](https://dk.farnell.com/)**, **POWER.dk**, **Dustin.dk** — Pi Zero 2 W (item 1) if raspberrypi.dk is out of stock.

Price comparison for the Pi: **[PriceRunner](https://www.pricerunner.dk/pl/10012-3208416724/Single-board-computere/Raspberry-Pi-Zero-2-W-Zero-2-Sammenlign-Priser)** (seen from ≈ 149 kr).

> **Rough total:** ≈ 700–1100 DKK for the electronics + tags, plus ≈ 300–600 DKK of
> tools if you're starting from zero. Filament/enclosure: already covered.

---

## Does it fit the Pi? (GPIO budget)

The Pi Zero 2 W has 26 usable GPIO. With 5 room slots and latching buttons (no LEDs)
this design needs **23** — it fits, with 3 pins to spare:

| Function | Pins | Suggested BCM (finalise at wiring) |
|----------|------|-----------------------------------|
| PN532 (I²C) | 2 | GPIO2 (SDA), GPIO3 (SCL) |
| 5× encoder (A/B) | 10 | 17/27, 22/23, 24/25, 12/16, 20/21 |
| 7× latching button (5 room, 2 mode) | 7 | 4, 5, 6, 13, 19, 26, 7 |
| 3× momentary button (transport) | 3 | 8, 9, 10 |
| Piezo buzzer (PWM) | 1 | GPIO18 (hardware PWM) |

(All buttons use internal pull-ups — no resistors. Latching buttons mean their GPIO
level directly reflects armed/active state, and the Pi reads them at boot. The 5 room
slots cover the 3 current speakers plus 2 for future expansion. A full wiring diagram
is the next hardware doc.)
