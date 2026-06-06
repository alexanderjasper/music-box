# Music Box

A phone-free way to control our Sonos speakers at home.

Place a physical card on the device, press play, and a corresponding album,
playlist, or radio station starts playing on one or more speakers. No screen to
get lost in, no app to open — just a tactile object and a button.

> **Status:** Scoping / idea phase. This README is a living design document.
> Nothing is built yet. Decisions marked **(open)** are still to be made.

---

## Motivation

When I'm home, I want to fully put my phone away. Today, playing music on our
3 Sonos speakers requires picking music or a radio station through the Sonos
app on my phone every single time. That pulls the phone back into my hand — and
my attention with it.

The Music Box replaces that with a physical, ambient interaction:

- Pick a card (album / playlist / radio station / mood).
- Place it on the box.
- Press play.
- Music plays on the speaker(s).

The phone stays away.

---

## Core concept

```
   [ physical card ]                  [ Sonos speakers ]
          │                                   ▲
          ▼                                   │
   ┌──────────────┐     local network /       │
   │  Music Box   │ ───── UPnP / API ─────────┘
   │  (no display)│
   │  buttons +   │
   │  card reader │
   └──────────────┘
          ▲
          │ configuration over Wi-Fi / Bluetooth
          │ (map card → music, no display needed on device)
   [ phone / laptop, only for setup ]
```

The phone is still allowed for **one-time configuration** (mapping a card to a
playlist). The goal is zero phone use for **everyday playback**.

---

## Goals

- **No general-purpose display.** Buttons only. Optionally a minimal display for
  track progress / time elapsed / volume — nothing you'd "browse".
- **Tactile cards** to select what plays.
- **One or more speakers** targetable per action (grouping).
- **Configuration off-device** — over local network and/or Bluetooth, from a
  phone or laptop.
- **Built from off-the-shelf electronics + 3D-printed enclosure** (Prusa Core One).
- Reliable and fast enough that it actually replaces the app for daily use.

## Non-goals (for now)

- Not trying to replicate the full Sonos app.
- No on-device music browsing/search.
- No cloud service of our own — keep everything local where possible.

---

## Open questions to scope together

These are the big decisions. We'll work through them and record the outcomes here.

### 1. Card technology **(open)**
How does the box recognize a card?
- **NFC tags** (e.g. RC522/PN532 reader + NTAG215 stickers in printed cards) —
  cheap, tiny, no battery, easy to encode an ID. Strong default.
- RFID (similar to NFC, slightly different frequency/range).
- Physical contacts / pin patterns / magnets + reed switches (fully offline,
  more mechanical, more printing).
- QR / barcode + camera (needs a camera + a little vision — heavier).

### 2. The "brain" **(open)**
What runs the logic and talks to Sonos?
- **Raspberry Pi Zero 2 W** — runs Linux + Python, easiest Sonos integration
  via the [SoCo](https://github.com/SoCo/SoCo) library, but boots slower and
  draws more power.
- **ESP32** — cheap, instant-on, low power, but Sonos control must be done over
  raw UPnP/HTTP and config/web UI is more work.
- Other (Pi 4/5, etc.) — overkill but flexible.

### 3. How we talk to Sonos **(open)**
- **Local UPnP control** (SoCo) — no internet dependency, works on the LAN.
- Sonos **favorites** as the unit of selection — easiest mapping target: a card
  → a Sonos favorite (which can be an album, playlist, or radio station).
- Music sources we care about: which services? (Spotify? Apple Music? TuneIn /
  internet radio? Local library?) **(open — need your list)**

### 4. Buttons & controls **(open)**
Minimum viable set:
- Play / pause
- Next / previous (?)
- Volume up / down
- Speaker / group selection (how? dedicated buttons? a card too?)

### 5. Display: none vs. minimal **(open)**
- None at all.
- Minimal: small OLED / e-ink showing track name + elapsed/remaining time +
  volume. Nice-to-have, not required for v1.

### 6. Configuration interface **(open)**
- Small **web app** served by the box on the LAN (open a page, see detected
  cards, assign each to a Sonos favorite). Works from any device.
- **Bluetooth** companion flow (more app-like, more work).
- Web app is the likely default; it's the least effort and most flexible.

### 7. Card ↔ action model **(open)**
What can a card encode?
- A specific favorite (album/playlist/station).
- A target speaker or group.
- A "mood" that maps to a rotating set.
- Just an ID; all meaning lives in the box's config (most flexible).

### 8. Power **(open)**
- USB-C wall power (simplest).
- Battery + charging (portable, more complexity).

---

## Likely architecture (first hypothesis, to be challenged)

> This is a starting point, **not** a committed decision.

- **Raspberry Pi Zero 2 W** running Python.
- **PN532 NFC reader** over SPI/I²C; cards are 3D-printed holders with an NFC
  sticker inside.
- **[SoCo](https://github.com/SoCo/SoCo)** for local Sonos control; cards map to
  **Sonos favorites**.
- A few **momentary push buttons** (play/pause, vol ±, next).
- Optional **small OLED** for track + time.
- A **local web app** (served from the Pi) for configuration: scan a card, pick
  the favorite + target speakers, save.
- **USB-C** powered.
- **3D-printed enclosure** with a card "slot" or "tray" and recessed buttons.

---

## Hardware (to be finalized)

| Part | Candidate | Notes |
|------|-----------|-------|
| Compute | Raspberry Pi Zero 2 W | Or ESP32 — see open question 2 |
| Card reader | PN532 / RC522 | NFC, see open question 1 |
| Cards | NTAG215 stickers in printed holders | Cheap, batteryless |
| Buttons | Momentary tactile switches | Count TBD |
| Display | SSD1306 OLED (optional) | Track + time only |
| Power | USB-C | TBD |
| Enclosure | 3D printed (Prusa Core One) | Cards slot/tray + buttons |

## Repository layout (planned)

```
/firmware or /software   # the code that runs on the device
/hardware                # wiring diagrams, BOM, pinouts
/cad                     # 3D models / STLs for the enclosure and cards
/docs                    # design notes, decisions, this scoping work
```

(Created as we go — empty for now.)

---

## Roadmap (rough)

1. **Decide the open questions above** (this phase).
2. **Spike**: get Python + SoCo controlling our actual Sonos speakers from a
   laptop — prove playback control end to end.
3. **Spike**: read an NFC card ID on the chosen brain.
4. Wire card → Sonos favorite → playback (breadboard, no enclosure).
5. Add buttons.
6. Build the config web app.
7. Design + print the enclosure and cards.
8. Assemble, polish, live with it, iterate.

---

## Notes / decisions log

_(We'll append dated decisions here as we lock them in.)_
