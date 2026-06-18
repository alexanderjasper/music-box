#!/usr/bin/env bash
# Push the code to the Pi without clobbering its live config.
#
# The box's web app writes the device's own state into cards.json (NFC tag ->
# favorite), rooms.json (slot -> Sonos room) and hardware.json (wiring). Those
# are written ON the Pi and must survive a code sync — otherwise every deploy
# wipes your enrolled cards. So they're excluded below; everything else mirrors.
#
# Usage:  ./sync.sh                      # defaults to alexander@musicbox.local
#         ./sync.sh pi@192.168.1.42      # or pass a different host
set -euo pipefail

HOST="${1:-alexander@musicbox.local}"
HERE="$(cd "$(dirname "$0")" && pwd)"

rsync -av \
  --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude 'cards.json' --exclude 'rooms.json' --exclude 'hardware.json' \
  "$HERE/" "$HOST:~/software/"
