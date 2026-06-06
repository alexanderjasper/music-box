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

### 2. The "brain" **(leaning Raspberry Pi — see findings)**
What runs the logic and talks to Sonos?
- **Raspberry Pi Zero 2 W** — runs Linux + Python, uses [SoCo] directly, hosts the
  config web app easily. The findings make this the strong default: SoCo is the
  proven, maintained path and needs a real OS. Boots slower / more power than an MCU,
  but for an always-on box that's fine.
- **ESP32** — cheap, instant-on, but would need raw UPnP reimplemented (no SoCo) and
  the config web app is more work. Findings push this *down* the list.
- Other (Pi 4/5, etc.) — overkill but flexible.

[SoCo]: https://github.com/SoCo/SoCo

### 3. How we talk to Sonos **(open)**
- **Local UPnP control** (SoCo) — no internet dependency, works on the LAN.
- Sonos **favorites** as the unit of selection — easiest mapping target: a card
  → a Sonos favorite (which can be an album, playlist, or radio station).
- Music sources we care about (**decided**, see findings below): **Apple Music**,
  **DR radio + DR podcasts** (via the **DR LYD** Sonos service). Other services
  can be added later. Podcasts beyond DR are a known gap — see findings.

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

## Technical findings: Sonos & Bluetooth (researched 2026-06-06)

A research pass into how the box can actually drive speakers. Sources are linked
at the bottom of this section.

### Two fundamentally different speaker models

This is the single most important realization, and it shapes the whole project:

- **Sonos = the box is a _controller_.** Sonos speakers are networked players that
  stream music *themselves* (directly from Apple Music's / DR's servers over your
  Wi-Fi). The box only sends commands like "play favorite X on the kitchen
  speaker." The box never touches the audio. This is lightweight, reliable, and
  a great fit for a small always-on device.
- **Bluetooth speaker = the box is the _audio source_.** A plain Bluetooth speaker
  has no idea what Apple Music is. The box itself would have to fetch, decode, and
  stream the audio over Bluetooth. That's a much heavier job — **and there is no
  good way to play Apple Music from a headless Linux device** (no official API /
  client). So **Bluetooth + Apple Music is effectively a dead end.** Bluetooth
  could work for *local files, internet radio, and podcast RSS streams*, but not
  our main source.

**Implication:** scope **v1 to Sonos only** (controller model). Bluetooth output
can be a *later, separate mode* limited to radio/podcasts/local files — not a
drop-in for Apple Music. ([Phoniebox] does BT this way, with local/Spotify audio.)

### How the box talks to Sonos

- **Local control via [SoCo]** (Python, UPnP over the LAN) is the recommended path.
  It is **actively maintained in 2026**, works on current Sonos S2 devices, and
  needs **no cloud account and no internet** for the control commands themselves.
- Sonos also has an **official cloud Control API**, but it requires OAuth + their
  cloud and has been less reliable (and the `getFavorites` cloud endpoint is
  reported as buggy). For an always-on local box, **local SoCo is the better bet.**
- SoCo handles the things we need: play/pause, next/prev, volume, **speaker
  grouping** (one or more speakers per action), and **listing/playing Sonos
  Favorites**.

### The Apple Music catch — and the workaround

- Apple Music on Sonos is an **account-linked service** using Sonos's SMAPI. Starting
  Apple Music playback *directly* by URI through SoCo / the API is **unreliable**
  (Apple Music, Spotify, Amazon are all flagged with auth/playback issues).
- **The robust pattern: Sonos Favorites.** You add the albums/playlists/stations you
  want to **My Sonos → Favorites** *once* in the Sonos app. The box then lists those
  favorites via SoCo and plays them by name. This sidesteps the broken
  direct-playback path and works across services.
- **Consequence for the card model:** each card maps to a **named Sonos Favorite**
  (+ a target speaker/group). Setup flow = "add it to Sonos Favorites, then assign a
  card to it" in our config web app. This scales fine to **100s of cards**.

### DR radio & podcasts — good news

- **DR LYD is a first-class Sonos music service** (Danish). It carries DR's **live
  radio channels, on-demand shows, _and_ podcasts**. So DR radio *and* DR podcasts
  are both reachable — save them as Sonos Favorites like anything else.
- **Podcasts outside DR are a gap.** Apple **Podcasts** is *not* a Sonos service, so
  non-DR podcasts can't be played the same way. Options if you want them later:
  other podcast services that *are* on Sonos, or playing a podcast's RSS audio URL
  directly. Noting this as a known limitation, not a v1 problem.

### Prior art worth studying

- **[Phoniebox] (RPi-Jukebox-RFID)** — mature Raspberry Pi + RFID jukebox; plug-and-play
  over USB, *no soldering required*, supports web radio/podcasts/Spotify and BT output.
  Great reference for the RFID + config-web-app + assembly approach, even though it
  targets local/Spotify rather than Sonos.
- **[zacharycohn/jukebox]** — a Raspberry Pi + NFC + **SoCo** Sonos jukebox. Closest to
  our concept; maps NFC tags → playlists. Confirms the SoCo approach works.

[SoCo]: https://github.com/SoCo/SoCo
[Phoniebox]: https://github.com/MiczFlor/RPi-Jukebox-RFID
[zacharycohn/jukebox]: https://github.com/zacharycohn/jukebox

---

## Likely architecture (first hypothesis, to be challenged)

> This is a starting point, **not** a committed decision.

- **Raspberry Pi Zero 2 W** running Python.
- **PN532 NFC reader** over SPI/I²C; cards are 3D-printed holders with an NFC
  sticker inside.
- **[SoCo](https://github.com/SoCo/SoCo)** for local Sonos control; each card maps
  to a **named Sonos Favorite** + target speaker/group (see findings above for why
  Favorites, not direct Apple Music URIs).
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

### 2026-06-06
- **Music sources for v1:** Apple Music, DR radio, DR podcasts (DR radio + podcasts
  both via the DR LYD Sonos service). Other services later.
- **Card count:** must scale to **100s** of cards.
- **Builder skill:** new to soldering/breadboarding but keen to learn → favor
  solder-free / plug-together modules where possible (e.g. Phoniebox-style).
- **Speaker target for v1:** **Sonos only** (controller model). Bluetooth output
  deferred to a possible later mode, and noted as **incompatible with Apple Music**.
- **Sonos control method:** local **SoCo** (UPnP, no cloud) is the chosen approach.
- **Card → action model:** each card = a **named Sonos Favorite** + target speaker/group.
  Pre-add content to Sonos Favorites once, then assign cards to favorites in config.
- **Brain:** leaning **Raspberry Pi Zero 2 W** (needed for SoCo + web config).
- **Known limitation:** non-DR podcasts (e.g. Apple Podcasts) aren't a Sonos service;
  out of scope for v1.
