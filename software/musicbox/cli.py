"""Interactive CLI that simulates the box's front panel.

Each command stands in for a physical control, so you can rehearse the real
interaction on a laptop:

    arm <room>        encoder push (arm/disarm a room)   e.g. `arm kok`
    vol <room> <n>    encoder turn (absolute 0-100)      e.g. `vol kok 25`
    vol <room> +/-n   encoder turn (relative)            e.g. `vol kok +5`
    shuffle [on|off]  shuffle toggle (no arg = flip)
    repeat  [on|off]  repeat toggle  (no arg = flip)
    card <id>         place a card on the spot           e.g. `card bohemian`
    eject             remove the card
    play              play/pause button
    next | prev       transport buttons
    rooms | cards | status | help | quit

Run:  python -m musicbox        (interactive)
"""

import sys

from .config import load_card_map
from .core import MusicBox
from .feedback import ConsoleBuzzer

PROMPT = "musicbox> "


def _emit(result):
    mark = "ok" if result["ok"] else "!!"
    print(f"  [{mark}] {result['message']}")


def _show_status(box):
    st = box.state()
    print("  ┌─ panel " + "─" * 32)
    for room in st["rooms"]:
        armed = "●" if room in st["armed"] else "○"
        vol = st["volumes"].get(room)
        vol_s = f"{vol:>3}" if vol is not None else "  ?"
        print(f"  │ {armed} {room:<16} vol {vol_s}")
    print(f"  │ shuffle {'ON ' if st['shuffle'] else 'off'}   repeat {'ON ' if st['repeat'] else 'off'}")
    card = st["current_card"]
    card_s = f"{card!r} -> {st['card_target']!r}" if card else "(none)"
    print(f"  │ card on spot: {card_s}")
    print(f"  │ playing: {st['playing']}")
    print("  └" + "─" * 39)


def _split(arg, n):
    parts = arg.split()
    return parts if len(parts) >= n else None


def run():
    card_map = load_card_map()
    box = MusicBox(card_map=card_map, buzzer=ConsoleBuzzer())
    print("Discovering Sonos speakers...")
    try:
        rooms = box.discover()
    except RuntimeError as e:
        sys.exit(str(e))
    print(f"Found: {', '.join(rooms)}")
    if card_map:
        print(f"Cards: {', '.join(sorted(card_map))}")
    else:
        print("No cards configured (copy cards.example.json to cards.json).")
    print("Type 'help' for commands, 'quit' to exit.\n")

    while True:
        try:
            line = input(PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        cmd, _, arg = line.partition(" ")
        cmd = cmd.lower()
        arg = arg.strip()

        if cmd in ("quit", "exit", "q"):
            break
        elif cmd in ("help", "?"):
            print(__doc__)
        elif cmd in ("rooms",):
            print("  " + ", ".join(box.rooms()))
        elif cmd in ("cards",):
            for cid, fav in sorted(box.card_map.items()):
                print(f"  {cid:<12} -> {fav}")
        elif cmd in ("status", "st", "s"):
            _show_status(box)
        elif cmd in ("arm", "a"):
            if arg:
                _emit(box.toggle_room(arg))
            else:
                print("  usage: arm <room>")
        elif cmd in ("vol", "v"):
            parts = _split(arg, 2)
            if not parts:
                print("  usage: vol <room> <0-100 | +n | -n>")
            elif parts[-1][0] in "+-":
                _emit(box.nudge_volume(" ".join(parts[:-1]), parts[-1]))
            else:
                _emit(box.set_volume(" ".join(parts[:-1]), parts[-1]))
        elif cmd == "shuffle":
            _emit(box.set_shuffle(arg.lower() == "on" if arg else not box.shuffle))
        elif cmd == "repeat":
            _emit(box.set_repeat(arg.lower() == "on" if arg else not box.repeat))
        elif cmd == "card":
            if arg:
                _emit(box.place_card(arg))
            else:
                print("  usage: card <id>")
        elif cmd in ("eject", "remove"):
            _emit(box.remove_card())
        elif cmd in ("play", "pause", "p"):
            _emit(box.play())
        elif cmd in ("next", "n"):
            _emit(box.next())
        elif cmd in ("prev", "previous", "b"):
            _emit(box.previous())
        else:
            print(f"  unknown command {cmd!r}; type 'help'")


if __name__ == "__main__":
    run()
