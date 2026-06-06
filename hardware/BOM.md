# Bill of Materials & where to buy

Everything needed to build the Music Box. You already have the **3D printer + filament**,
so all knobs, button caps and the enclosure are printed (free). Prices are indicative
(incl. VAT) and will vary — check current listings. Quantities are for the agreed design:
**up to 5 rooms** (3 speakers today + 2 spare slots for future expansion), NFC cards, no
display.

> **Recommended: one order from [BerryBase.de](https://www.berrybase.de/en/).** It stocks
> essentially every part below, cheaply, and ships from Germany to Denmark with **no
> customs** (EU). A single BerryBase order covers the whole electronics build (specific SKUs chosen for the
> controls — see items 6–8) for roughly **€55–75**. The **Buy** column lists BerryBase
> first, with Danish shops as alternates if something's out of stock. Two picks still
> need care — see the ⚠️ flags on the PSU (≥2.5 A) and the PN532 (module, not HAT).

> New to soldering? The **WH** board has its 40-pin header pre-soldered, so the Pi needs
> none. Encoders, buttons, the buzzer and the NFC module still need a few solder joints
> for the final build — but start on a **breadboard** first (no soldering) to prove the
> wiring.

## Core electronics

| # | Part | Qty | ≈ price | Buy (BerryBase first, DK alt.) | Notes |
|---|------|-----|------|-----|-------|
| 1 | **Raspberry Pi Zero WH** (or **Zero 2 WH**) — pre-soldered header | 1 | €18–25 | [BerryBase Zero WH](https://www.berrybase.de/en/raspberry-pi-zero-wh) · [raspberrypi.dk (2 WH)](https://raspberrypi.dk/en/product/raspberry-pi-zero-2-wh-with-presoldered-header/) | The brain. **WH** = no header soldering. Original **Zero W is fine for Sonos-only**; the quad-core **Zero 2** is only worth chasing if you later want the Pi to play Bluetooth audio itself. The Pi is swappable later (same header, SD card moves over). |
| 2 | microSD card 16–32 GB (A1) | 1 | €6–9 | [BerryBase (SanDisk Ultra)](https://www.berrybase.de/en/) · [raspberrypi.dk](https://raspberrypi.dk/en/shop/category/sd-cards-adapters/) | Runs Raspberry Pi OS Lite. Use a genuine SanDisk/Samsung — cheap fakes corrupt on boot. |
| 3 | **5V micro-USB PSU (≥2.5A)** ⚠️ | 1 | €8–12 | [official Pi PSU](https://www.raspberrypi.com/products/micro-usb-power-supply/) (BerryBase & raspberrypi.dk stock it) | Pi Zero uses **micro-USB** (not USB-C). ⚠️ **Don't buy a 1 A adapter** — even the Zero W browns out under Wi-Fi. Get ≥2.5 A (official PSU is ideal). |
| 4 | **PN532 NFC module** (I²C/SPI/UART) ⚠️ | 1 | €7–12 | [BerryBase module (+card+dongle)](https://www.berrybase.de/en/pn532-nfc-und-rfid-modul-inkl.-karte-dongle) · [bitbyg](https://bitbyg.dk/shop/pn532-nfc-rfid-module-v3/) · [arduinotech](https://arduinotech.dk/nfc-pn532-modul-brik/) | Reads the cards over I²C (2 wires + power). ⚠️ Get the **module**, *not* the [PN532 HAT](https://www.berrybase.de/en/pn532-nfc-hat-for-raspberry-pi-i2c-spi-uart) — the HAT occupies the 40-pin header we need for buttons/encoders. |
| 5 | **NTAG215 NFC tags** (25 mm, self-adhesive) | 5–10 packs of 10 | €3–5 /pack | [BerryBase (self-adhesive ×10)](https://www.berrybase.de/en/rfid-nfc-tags-ntag215-25mm-self-adhesive-white-10-pieces) · [plain ×10](https://www.berrybase.de/en/rfid-nfc-tags-ntag215-25mm-white-10-pieces) · [idekort (bulk)](https://idekort.dk/vare-kategori/rfid-og-kontaktloese-kort-og-brikker/nfc-ntag-produkter/) | One per card. Self-adhesive ø25 mm stickers embed easily in a printed card. We only read the **UID**, so cheap tags are fine. |

## Controls (the panel)

| # | Part | Qty | ≈ price | Buy (BerryBase first, DK alt.) | Notes |
|---|------|-----|------|-----|-------|
| 6 | **KY-040 rotary encoder** w/ breakout (6 mm knurled shaft, with thread & nut) | 5 | €1.60 ea | [BerryBase](https://www.berrybase.de/en/rotary-encoder-with-breakout-board) | One volume knob per room slot (3 used + 2 spare). 20 pulses/rev, onboard pull-ups, threaded bushing for panel mount. Pins CLK(A)/DT(B)/SW/+/GND — we use CLK, DT, GND (ignore SW). Print the knobs. |
| 7 | **DSQ14 latching push-switch**, square 14×14 mm (push-on/push-off) | 7 | from €0.77 ea | [BerryBase](https://www.berrybase.de/druckschalter-quadratisch-schliesser) | 5 room-arm + shuffle + repeat. **Latching** (2-position, *rastend*) — the cap **stays pressed in when active**, so position *is* the state (no LED) and it holds across power-off. 12 mm panel hole, SPST-NO (closed when in → active-LOW, matches `WIRING.md`). Fixed cap: label with a sticker / print a thin symbol cap. |
| 8 | **Mikro-Drucktaster 12 mm round**, momentary | 3 | ~€0.50 ea | [BerryBase](https://www.berrybase.de/en/micro-push-button-12mm-round-pcb-mounting-no-contact/) | Previous / play-pause / next — **momentary** (*Schließer*, springs back). Comes in colours (give Play a distinct one + a printed combined ▶❚❚ cap). |
| 9 | **KY-006 passive buzzer module** | 1 | €1.10 | [BerryBase](https://www.berrybase.de/ky-006-passives-buzzer-modul) | Audio feedback (chirps/error). **Passive** (PWM plays tones), 3-pin module: **S → GPIO18**, **− → GND** (middle pin unused). Beginner-friendly. *Not* the active "Signalgeber" / "16 tones" types, which only play one fixed tone. |

## Wiring & passives

| # | Part | Qty | ≈ price | Buy (BerryBase first, DK alt.) | Notes |
|---|------|-----|------|-----|-------|
| 10 | Breadboard (830-point) | 1 | €2–6 | [BerryBase (830)](https://www.berrybase.de/breadboard-mit-830-kontakten) · [arduinotech](https://arduinotech.dk/shop/breadboard-830-points/) | Prototype before soldering. |
| 11 | Jumper wires (M-F, M-M, F-F kit) | 1 | €3–8 | [BerryBase (65-cable kit)](https://www.berrybase.de/jumper-kabel-kit-set-mit-65-kabeln-in-4-laengen-fuer-breadboards) · [let-elektronik](https://let-elektronik.dk/breadboard-jumper-wire-kit-140pcs) | For breadboarding and Pi connections. |
| 12 | Hook-up / silicone wire (thin, ~26 AWG) | 1 | €4–6 | [BerryBase (prototyping)](https://www.berrybase.de/en/components/prototyping/jumper-cable/) · [arduinotech](https://arduinotech.dk/produkt-kategori/tilbehor/ledning-jump-wire-mm/) | For the final soldered build. |
| 13 | (Optional) Resistor assortment | 1 kit | €5–8 | [let-elektronik (modstande)](https://let-elektronik.dk/modstande) | Buttons use the Pi's internal pull-ups, so likely none needed for v1. Handy to have. |
| 14 | (Optional) Pi Zero proto/HAT board | 1 | €4–8 | [BerryBase (permanent 830 PCB)](https://www.berrybase.de/permanent-pcb-breadboard-mit-830-kontakten-schwarz) · [raspberrypi.dk](https://raspberrypi.dk/en/shop/category/raspberry-pi-zero-and-accessories/) | Tidy permanent wiring instead of loose solder. |

## Tools (if you don't have them)

| # | Part | ≈ DKK | Buy | Notes |
|---|------|------|-----|-------|
| 15 | Temperature-controlled soldering iron + solder | 200–450 | [Kjell & Company](https://www.kjell.com/dk) | Kjell has these in-store (walk-in). A basic 60W is fine to learn on. |
| 16 | Wire stripper / side cutters | 60–120 | [Kjell & Company](https://www.kjell.com/dk) | |
| 17 | (Nice) Multimeter | 80–200 | [Kjell & Company](https://www.kjell.com/dk) | For checking connections/continuity. |

## 3D printed (you make these — no purchase)

- Enclosure (case + faceplate with holes for buttons, encoders, card spot, buzzer grille).
- 3 knobs (fit EC11 6 mm knurled shaft).
- Button caps — incl. multi-material/multi-colour **shuffle/repeat symbol caps** and the
  **room-name caps** if you print labels rather than apply stickers.
- A card spot/tray and the cards themselves (NTAG215 sticker inside each).

---

## Where to buy

**Recommended — one EU order, ships to DK, no customs:**
- **[BerryBase.de](https://www.berrybase.de/en/)** — stocks the Pi board, PN532, NTAG215
  packs, encoders, switches, piezo, breadboard and wires: the **whole electronics build in
  one order** (the **Buy** column above links each item). Ships from Germany.

**Danish, fast (good alternates / pickup):**
- **[raspberrypi.dk](https://raspberrypi.dk/)** — Pi Zero 2 W (WH), microSD, official PSU, case (items 1–3).
- **[let-elektronik.dk](https://let-elektronik.dk/rfid-nfc-tags-sensorer)** — wide hobby range: PN532/NFC, encoders, buttons, buzzer, breadboard, jumpers, resistors (items 4, 6–13).
- **[elektronik-lavpris.dk](https://elektronik-lavpris.dk/)** — general hobby electronics, often cheap (PN532, buttons, passives).
- **[bitbyg.dk](https://bitbyg.dk/shop/pn532-nfc-rfid-module-v3/)** / **[ebits.dk](https://ebits.dk/products/pn532-rfid-laeser-inkl-noglekort-og-noglebrik)** — PN532 module.
- **[idekort.dk](https://idekort.dk/vare-kategori/rfid-og-kontaktloese-kort-og-brikker/nfc-ntag-produkter/)** — bulk NTAG213/215/216 tags & cards (item 5).
- **[arduinotech.dk](https://arduinotech.dk/shop/ntag-rfid-nfc-tag-smartphones/)** — NTAG215 tags, Arduino-style modules.
- **Kjell & Company** (kjell.com/dk, **physical stores** in DK) — soldering iron, wires, tools (items 15–17) you can pick up today.

**If the Pi is out of stock everywhere:** check **[amazon.de](https://www.amazon.de/Raspberry-Pi%C2%AE-Zero-512-1-0/dp/B0DB2JBD9C)**
(watch for third-party markup over RRP), **[Farnell](https://dk.farnell.com/)**, **POWER.dk**,
**Dustin.dk**, or compare on **[PriceRunner](https://www.pricerunner.dk/pl/10012-3208416724/Single-board-computere/Raspberry-Pi-Zero-2-W-Zero-2-Sammenlign-Priser)**.

> **Rough total:** **≈ €55–75** for the electronics + tags in one BerryBase order, plus
> **≈ 300–600 DKK** of tools if you're starting from zero. Filament/enclosure: already covered.

---

## Does it fit the Pi? (GPIO budget)

The Pi Zero W and Zero 2 W share the same 40-pin header — **26 usable GPIO**. With 5 room
slots and latching buttons (no LEDs) this design needs **23** — it fits, with 3 to spare:

| Function | Pins | Suggested BCM (finalise at wiring) |
|----------|------|-----------------------------------|
| PN532 (I²C) | 2 | GPIO2 (SDA), GPIO3 (SCL) |
| 5× encoder (A/B) | 10 | 17/27, 22/23, 24/25, 12/16, 20/21 |
| 7× latching button (5 room, 2 mode) | 7 | 4, 5, 6, 13, 19, 26, 7 |
| 3× momentary button (transport) | 3 | 8, 9, 10 |
| Piezo buzzer (PWM) | 1 | GPIO18 (hardware PWM) |

(All buttons use internal pull-ups — no resistors. Latching buttons mean their GPIO
level directly reflects armed/active state, and the Pi reads them at boot. The 5 room
slots cover the 3 current speakers plus 2 for future expansion. The exact pin-to-pin
connections are in **[`WIRING.md`](WIRING.md)**.)
