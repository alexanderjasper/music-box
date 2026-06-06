"""Loading the card -> favorite mapping.

For now this is a simple JSON file: card id -> a substring of the Sonos Favorite
title to play. The card id stands in for what will later be an NFC tag UID. The
config web app will eventually edit this file; today you edit it by hand.
"""

import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the software/ dir


def load_card_map(path=None):
    """Load cards.json, falling back to cards.example.json. Ignores _-prefixed keys."""
    if path is None:
        for candidate in ("cards.json", "cards.example.json"):
            p = os.path.join(HERE, candidate)
            if os.path.exists(p):
                path = p
                break
    if not path or not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}
