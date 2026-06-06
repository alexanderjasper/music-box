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
> first, with Danish shops as alternates if something's out of stock. One pick still
> needs care — see the ⚠️ flag on the PN532 (get the **module**, not the HAT, which would
> occupy our GPIO header).

> New to soldering? The **WH** board has its 40-pin header pre-soldered, so the Pi needs
> none. Encoders, buttons, the buzzer and the NFC module still need a few solder joints
> for the final build — but start on a **breadboard** first (no soldering) to prove the
> wiring.

## Core electronics

| # | Part | Qty | ≈ price | Buy (BerryBase first, DK alt.) | Notes |
|---|------|-----|------|-----|-------|
| 1 | **Raspberry Pi Zero WH** (or **Zero 2 WH**) — pre-soldered header | 1 | €18–25 | [BerryBase Zero WH](https://www.berrybase.de/en/raspberry-pi-zero-wh) · [raspberrypi.dk (2 WH)](https://raspberrypi.dk/en/product/raspberry-pi-zero-2-wh-with-presoldered-header/) | The brain. **WH** = no header soldering. Original **Zero W is fine for Sonos-only**; the quad-core **Zero 2** is only worth chasing if you later want the Pi to play Bluetooth audio itself. The Pi is swappable later (same header, SD card moves over). |
| 2 | microSD card **16 GB, A1** (32 GB fine) | 1 | €7–16 | [BerryBase Pi memory cards](https://www.berrybase.de/en/raspberry-pi/raspberry-pi-computer/memory-cards/) · [SanDisk Ultra 32GB (€15.60)](https://www.berrybase.de/en/sandisk-ultra-microsdhc-a1-120mb/s-class-10-speicherkarte-adapter-32gb) | Runs Raspberry Pi OS Lite (~4 GB), so **16 GB is plenty** — 32 GB is overkill. Must be **A1** (random-I/O = a responsive Pi); genuine SanDisk only (fakes corrupt on boot). Reuse any ≥8 GB A1 card you own to save the cost. |
| 3 | **5V micro-USB PSU, 2.5A** | 1 | €8–12 | [BerryBase Pi micro-USB PSU 5V/2.5A](https://www.berrybase.de/micro-usb-netzteil-fuer-raspberry-pi-5v/2-5a-schwarz) | Pi Zero uses **micro-USB** (not USB-C). This one is **2.5 A** — don't substitute a 1 A adapter (browns out under Wi-Fi). |
| 4 | **PN532 NFC module** (I²C/SPI/UART) ⚠️ | 1 | €7–12 | [BerryBase module (+card+dongle)](https://www.berrybase.de/en/pn532-nfc-und-rfid-modul-inkl.-karte-dongle) · [bitbyg](https://bitbyg.dk/shop/pn532-nfc-rfid-module-v3/) · [arduinotech](https://arduinotech.dk/nfc-pn532-modul-brik/) | Reads the cards over I²C (2 wires + power). ⚠️ Get the **module**, *not* the [PN532 HAT](https://www.berrybase.de/en/pn532-nfc-hat-for-raspberry-pi-i2c-spi-uart) — the HAT occupies the 40-pin header we need for buttons/encoders. |
| 5 | **NTAG215 NFC tags** (25 mm, self-adhesive) | 5–10 packs of 10 | €3–5 /pack | [BerryBase (self-adhesive ×10)](https://www.berrybase.de/en/rfid-nfc-tags-ntag215-25mm-self-adhesive-white-10-pieces) · [plain ×10](https://www.berrybase.de/en/rfid-nfc-tags-ntag215-25mm-white-10-pieces) · [idekort (bulk)](https://idekort.dk/vare-kategori/rfid-og-kontaktloese-kort-og-brikker/nfc-ntag-produkter/) | One per card. Self-adhesive ø25 mm stickers embed easily in a printed card. We only read the **UID**, so cheap tags are fine. |

## Controls (the panel)

| # | Part | Qty | ≈ price | Buy (BerryBase first, DK alt.) | Notes |
|---|------|-----|------|-----|-------|
| 6 | **KY-040 rotary encoder** w/ breakout (6 mm knurled shaft, with thread & nut) | 5 | €1.60 ea | [BerryBase](https://www.berrybase.de/en/rotary-encoder-with-breakout-board) | One volume knob per room slot (3 used + 2 spare). 20 pulses/rev, onboard pull-ups, threaded bushing for panel mount. Pins CLK(A)/DT(B)/SW/+/GND — we use CLK, DT, GND (ignore SW). Print the knobs. |
| 7 | **DSQ14 latching push-switch**, square 14×14 mm (push-on/push-off) | 7 | from €0.77 ea | [BerryBase](https://www.berrybase.de/druckschalter-quadratisch-schliesser) | 5 room-arm + shuffle + repeat. **Latching** (2-position, *rastend*) — the cap **stays pressed in when active**, so position *is* the state (no LED) and it holds across power-off. 12 mm panel hole, SPST-NO (closed when in → active-LOW, matches `WIRING.md`). Fixed cap: label with a sticker / print a thin symbol cap. |
| 8 | **Square push-button** (Drucktaster quadratisch), momentary, 14×14 mm | 3 | ~€0.80 ea | [BerryBase](https://www.berrybase.de/drucktaster-quadratisch-schliesser) | Previous / play-pause / next — **momentary** (*Schließer*, springs back). **Same 14×14 mm body + 12 mm panel hole as the DSQ14 latching switches** (item 7), so the whole panel matches and wires identically. (The 12 mm round *PCB-mount* button is smaller and not panel-friendly — avoid for the faceplate.) |
| 9 | **KY-006 passive buzzer module** | 1 | €1.10 | [BerryBase](https://www.berrybase.de/ky-006-passives-buzzer-modul) | Audio feedback (chirps/error). **Passive** (PWM plays tones), 3-pin module: **S → GPIO18**, **− → GND** (middle pin unused). Beginner-friendly. *Not* the active "Signalgeber" / "16 tones" types, which only play one fixed tone. |

## Wiring & passives

| # | Part | Qty | ≈ price | Buy (BerryBase first, DK alt.) | Notes |
|---|------|-----|------|-----|-------|
| 10 | Breadboard (830-point) | 1 | €2–6 | [BerryBase (830)](https://www.berrybase.de/breadboard-mit-830-kontakten) · [arduinotech](https://arduinotech.dk/shop/breadboard-830-points/) | Prototype before soldering. |
| 11 | Dupont jumper set, 40-pin **F-F / M-M / F-M**, 20 cm | 1 | €4.90 | [BerryBase Dupont set](https://www.berrybase.de/en/40pin-jumper-dupont-cable-set-1x-f-f-m-m-f-m-each-20cm) | **Essential:** the Pi Zero header is **male**, so you need **F-M** wires to reach the breadboard — a plain M-M kit can't. This set has all three types. (Optional extra: the [65-cable solid M-M kit](https://www.berrybase.de/jumper-kabel-kit-set-mit-65-kabeln-in-4-laengen-fuer-breadboards) for tidy breadboard runs.) |
| 12 | Hook-up wire, 0.14 mm² (10 m spool) | 1–2 | €1.50 ea | [BerryBase Kupferlitze 10m (black)](https://www.berrybase.de/kupferlitze-isoliert-1x0-14mm-10m/farbe-schwarz) | Single-strand insulated wire for the final soldered build. One 10 m spool is enough length; a **2nd colour for ground** (e.g. black=GND + one other) makes wiring much easier to trace. (Or the [10-colour set](https://www.berrybase.de/kupferlitze-isoliert-0-14-mm2-set-10x10m) if you want the full rainbow.) |
| 13 | (Optional) Resistor assortment, 525-pc | 1 kit | €6–9 | [BerryBase 525-pc metal-film set](https://www.berrybase.de/525-teiliges-metallschichtwiderstands-sortiment-in-kunststoffbox/) | Buttons use the Pi's internal pull-ups, so likely none needed for v1. Handy to have. |
| 14 | (Optional) Pi Zero proto/HAT board | 1 | €4–8 | [BerryBase (permanent 830 PCB)](https://www.berrybase.de/permanent-pcb-breadboard-mit-830-kontakten-schwarz) · [raspberrypi.dk](https://raspberrypi.dk/en/shop/category/raspberry-pi-zero-and-accessories/) | Tidy permanent wiring instead of loose solder. |

## Tools (if you don't have them)

| # | Part | ≈ price | Buy | Notes |
|---|------|------|-----|-------|
| 15 | Soldering station (temp-controlled) | €33 | [BerryBase goobay AP2 analog station, 48W](https://www.berrybase.de/goobay-ap2-analoge-loetstation-48w/) | Dial temperature control + stand — the right amount of tool for this. Step up: [Fixpoint EP5 digital](https://www.berrybase.de/en/fixpoint-ep5-digital-soldering-station-with-set-and-actual-temperature-display) (€75). Step down: [4-pc 30W set](https://www.berrybase.de/4-teiliges-loetset-bestehend-aus-30w-loetkolben-entloetpumpe-loetkolbenablage) (unregulated). |
| 16 | Solder, lead-free | €3–15 | [goobay 1.0mm 17g dispenser (~€3)](https://www.berrybase.de/goobay-loetzinn-bleifrei-oe1-0mm) · [0.56mm 100g roll (~€15)](https://www.berrybase.de/goobay-loetzinn-bleifrei-oe0-56mm-100g-rolle) | You only need a little for one box, so the small **17 g dispenser** is enough (1.0 mm = slightly thick). The **0.56 mm 100 g roll** is thinner/easier and a buy-once. (Lead-free silver solder runs pricey — don't be surprised by larger rolls at €25+.) |
| 17 | Wire stripper + side cutter | €6–12 | [BerryBase auto stripper + cutter](https://www.berrybase.de/en/automatik-abisolierzange-mit-integriertem-kabelschneider) | Strips and cuts in one tool. |
| 18 | (Nice) Multimeter | €15–30 | [BerryBase UNI-T UT131A](https://www.berrybase.de/uni-t-ut131a-digitales-multimeter-palm-size-mit-2mf-kapazitaetsmessung) | For continuity / voltage checks. Kjell (walk-in in DK) is a fine alternative. |
| 19 | (Optional) Desoldering pump | €2–4 | [BerryBase Entlötpumpe](https://www.berrybase.de/en/entloetpumpe-mit-hoher-saugleistung-teflonspitze) | Fixes solder blobs/bridges — handy while learning. |

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
- **Kjell & Company** (kjell.com/dk, **physical stores** in DK) — soldering iron, wires, tools (items 15–18) if you'd rather walk in and buy today than wait for the BerryBase order.

**If the Pi is out of stock everywhere:** check **[amazon.de](https://www.amazon.de/Raspberry-Pi%C2%AE-Zero-512-1-0/dp/B0DB2JBD9C)**
(watch for third-party markup over RRP), **[Farnell](https://dk.farnell.com/)**, **POWER.dk**,
**Dustin.dk**, or compare on **[PriceRunner](https://www.pricerunner.dk/pl/10012-3208416724/Single-board-computere/Raspberry-Pi-Zero-2-W-Zero-2-Sammenlign-Priser)**.

> **Rough total:** **≈ €55–75** for the electronics + tags, plus **≈ €40–95** of tools if
> you're starting from zero — all in a single BerryBase order. Filament/enclosure: already covered.

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
