#!/usr/bin/env python3
"""Music Box — Sonos spike.

The point of this script is to de-risk the whole project *before* buying any
hardware. It proves three things against your real speakers, over your local
network, with no Sonos cloud account and no internet dependency:

  1. We can discover your Sonos speakers.            ->  `discover`
  2. We can read your Sonos Favorites.               ->  `favorites`
  3. We can start one playing on a chosen speaker.   ->  `play`

The critical test is step 3 with an **Apple Music** favorite: if that plays,
the "can we even control Apple Music?" risk is gone.

SETUP (on your laptop, same Wi-Fi as the speakers):

    cd software
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

USAGE:

    python spike_sonos.py discover
    python spike_sonos.py favorites
    python spike_sonos.py play --room "Kitchen" --favorite "Morning Jazz"
    python spike_sonos.py play --room "Kitchen" --index 0
    python spike_sonos.py status --room "Kitchen"

Tip: run `favorites` first to see the exact names to pass to `play`. Add some
albums / playlists / DR LYD stations to "My Sonos -> Favorites" in the Sonos
app beforehand so there's something to play.
"""

import argparse
import sys

try:
    import soco
    from soco.exceptions import SoCoException
except ImportError:
    sys.exit(
        "The 'soco' package isn't installed.\n"
        "Run:  pip install -r requirements.txt   (inside your venv)"
    )


def discover_speakers():
    """Return a list of Sonos devices on the network, or exit with help."""
    speakers = soco.discover()
    if not speakers:
        sys.exit(
            "No Sonos speakers found.\n"
            "Checklist:\n"
            "  - this computer is on the SAME Wi-Fi / subnet as the speakers\n"
            "  - the speakers are powered on\n"
            "  - your firewall isn't blocking UPnP/SSDP (UDP 1900)\n"
        )
    return list(speakers)


def get_room(name):
    """Find a speaker (zone) by its room name, case-insensitive."""
    for speaker in discover_speakers():
        if speaker.player_name.lower() == name.lower():
            return speaker
    rooms = ", ".join(sorted(s.player_name for s in discover_speakers()))
    sys.exit(f"No speaker named {name!r}. Available rooms: {rooms}")


def cmd_discover(_args):
    print("Discovered Sonos speakers:\n")
    for s in sorted(discover_speakers(), key=lambda s: s.player_name):
        coordinator = " (group coordinator)" if s.is_coordinator else ""
        print(f"  - {s.player_name:<20} {s.ip_address}{coordinator}")


def cmd_favorites(_args):
    # Favorites are household-wide, so any one speaker can report them.
    speaker = discover_speakers()[0]
    favorites = speaker.music_library.get_sonos_favorites()
    if not favorites:
        print(
            "No Sonos Favorites found.\n"
            "Open the Sonos app -> My Sonos -> add an album/playlist/station "
            "to Favorites, then re-run this."
        )
        return
    print(f"Sonos Favorites ({favorites.total_matches} total):\n")
    for i, fav in enumerate(favorites):
        print(f"  [{i}] {fav.title}")


def cmd_play(args):
    speaker = get_room(args.room)
    favorites = list(speaker.music_library.get_sonos_favorites())
    if not favorites:
        sys.exit("No favorites to play. Add some in the Sonos app first.")

    if args.index is not None:
        if not 0 <= args.index < len(favorites):
            sys.exit(f"Index {args.index} out of range (0..{len(favorites) - 1}).")
        chosen = favorites[args.index]
    else:
        matches = [f for f in favorites if args.favorite.lower() in f.title.lower()]
        if not matches:
            names = "\n".join(f"  - {f.title}" for f in favorites)
            sys.exit(f"No favorite matching {args.favorite!r}. Favorites:\n{names}")
        chosen = matches[0]

    print(f"Playing {chosen.title!r} on {speaker.player_name!r} ...")
    # A favorite carries the resource + the metadata Sonos needs to authorize the
    # stream. This is the path that works for account-linked services (Apple Music,
    # DR LYD) where raw URIs do not.
    speaker.play_uri(chosen.resources[0].uri, meta=chosen.resource_meta_data)
    print("Sent. If it's quiet, check the speaker's volume.")


def cmd_status(args):
    speaker = get_room(args.room)
    track = speaker.get_current_track_info()
    state = speaker.get_current_transport_info()["current_transport_state"]
    print(f"Room:     {speaker.player_name}")
    print(f"State:    {state}")
    print(f"Track:    {track.get('title') or '(none)'}")
    print(f"Artist:   {track.get('artist') or ''}")
    print(f"Position: {track.get('position')} / {track.get('duration')}")
    print(f"Volume:   {speaker.volume}")


def main():
    parser = argparse.ArgumentParser(description="Music Box — Sonos spike")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("discover", help="list speakers on the network")
    sub.add_parser("favorites", help="list your Sonos Favorites")

    p_play = sub.add_parser("play", help="play a favorite on a room")
    p_play.add_argument("--room", required=True, help="speaker/room name")
    group = p_play.add_mutually_exclusive_group(required=True)
    group.add_argument("--favorite", help="favorite name (substring match)")
    group.add_argument("--index", type=int, help="favorite index from `favorites`")

    p_status = sub.add_parser("status", help="show what a room is playing")
    p_status.add_argument("--room", required=True, help="speaker/room name")

    args = parser.parse_args()
    handlers = {
        "discover": cmd_discover,
        "favorites": cmd_favorites,
        "play": cmd_play,
        "status": cmd_status,
    }
    try:
        handlers[args.command](args)
    except SoCoException as e:
        sys.exit(f"Sonos error: {e}")


if __name__ == "__main__":
    main()
