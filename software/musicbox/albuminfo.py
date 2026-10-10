"""Artist, album title and track list for a card's back label.

Sonos hands over very little about a favorite: a title, and for Apple Music an
item id with the catalogue number in it (`1004206calbum%3a1440857781`). That
number is enough for Apple's public lookup API, which needs no account and gives
the album's tracks in order. Playlists (`playlist%3apl.b833…`) aren't in that
API, so their tracks come from the public music.apple.com page instead, which
carries them as schema.org data. Without an id (an album from your own library,
a service other than Apple's) it falls back to searching the catalogue by title,
and only takes an exact name match — a confident wrong track list is worse than
an empty one the label page asks you to fill in.

Everything returned is a suggestion: the label page shows it in editable fields.
"""

import collections
import json
import os
import re
import unicodedata
import urllib.parse
import urllib.request

# Apple's catalogue differs per country, and lookups by id only find what the
# storefront sells. The box is in Denmark; MUSICBOX_STOREFRONT overrides that.
STOREFRONT = os.environ.get("MUSICBOX_STOREFRONT", "dk")
API = "https://itunes.apple.com"
WEB = "https://music.apple.com"

_ID_RE = re.compile(r"(album|song|playlist)(?:%3a|:)(pl\.[\w.-]+|\d+)", re.I)
_EDITION_RE = re.compile(r"\s+-\s+(Single|EP)$", re.I)
_COLLAB_RE = re.compile(r"\s*(?:&|,|\bfeat\.?|\bft\.|\bwith\b|\bx\b)\s*", re.I)


def apple_id(*texts):
    """('album' | 'song' | 'playlist', id) from Sonos ids or URIs, or None."""
    for text in texts:
        m = _ID_RE.search(text or "")
        if m and (m.group(1).lower() == "playlist") == m.group(2).startswith("pl."):
            return m.group(1).lower(), m.group(2)
    return None


def lead_artist(artists):
    """The artist most of the tracks are by, duets included, or "".

    "Lille Bille & Pharfar" counts for Lille Bille. Under half the tracks and
    it's a mix, which gets no artist line rather than a misleading one.
    """
    leads = [_COLLAB_RE.split(a, maxsplit=1)[0].strip() for a in artists if a]
    if not leads:
        return ""
    name, count = collections.Counter(leads).most_common(1)[0]
    return name if count * 2 >= len(artists) else ""


def tracklist(tracks):
    """(artist, track lines) from [(title, artist)]: titles alone under a lead
    artist, "Title – Artist" for a mix, where who sings it is worth printing."""
    artist = lead_artist([a for _, a in tracks])
    if artist:
        return artist, [t for t, _ in tracks]
    return "", [f"{t} \u2013 {a}" if a else t for t, a in tracks]


def _get(path, **params):
    params.setdefault("country", STOREFRONT)
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=8) as r:
        return json.load(r).get("results", [])


def _album_name(name):
    return _EDITION_RE.sub("", name or "")


def _fold(s):
    s = unicodedata.normalize("NFKD", s or "").casefold()
    return "".join(c for c in s if c.isalnum())


def lookup_album(collection_id):
    results = _get("lookup", id=collection_id, entity="song")
    album = next((r for r in results if r.get("wrapperType") == "collection"), None)
    if album is None:
        return None
    songs = sorted((r for r in results if r.get("wrapperType") == "track"
                    and r.get("kind", "song") == "song"),  # not the bonus videos
                   key=lambda r: (r.get("discNumber", 1), r.get("trackNumber", 0)))
    return {"artist": album.get("artistName", ""),
            "album": _album_name(album.get("collectionName")),
            "tracks": [s.get("trackName", "") for s in songs]}


def lookup_song(track_id):
    song = next(iter(_get("lookup", id=track_id)), None)
    if song is None:
        return None
    return {"artist": song.get("artistName", ""),
            "album": song.get("trackName", ""),
            "tracks": [song.get("trackName", "")]}


def _page(path):
    req = urllib.request.Request(f"{WEB}/{STOREFRONT}/{path}",
                                 headers={"User-Agent": "Mozilla/5.0 (music-box)"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", "replace")


def _script(html, attrs):
    m = re.search(rf"<script[^>]*{attrs}[^>]*>(.*?)</script>", html, re.S)
    return json.loads(m.group(1)) if m else None


def lookup_playlist(playlist_id):
    """An Apple Music playlist's name, tracks and their artists.

    The page's schema.org block is the stable part and gives the tracks in
    order. Artists only sit in the app's own server data, matched up by track
    title; a track it doesn't name just goes without. A private playlist has no
    public page, and errors like any other failed lookup.
    """
    html = _page(f"playlist/{playlist_id}")
    ld = _script(html, r'type="application/ld\+json"')
    if not ld or not ld.get("track"):
        return None
    titles = [t.get("name", "") for t in ld["track"]]
    artists = {}
    def walk(o):
        if isinstance(o, dict):
            if "artistName" in o and o.get("title"):
                artists.setdefault(o["title"], o["artistName"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    try:
        walk(_script(html, r'id="serialized-server-data"'))
    except ValueError:
        pass
    artist, tracks = tracklist([(t, artists.get(t, "")) for t in titles])
    return {"artist": artist, "album": ld.get("name", ""), "tracks": tracks}


def search_album(title, artist=""):
    """The catalogue album named exactly `title` (by `artist`, if given)."""
    term = f"{title} {artist}".strip()
    for hit in _get("search", term=term, entity="album", limit=25):
        if _fold(_album_name(hit.get("collectionName"))) != _fold(title):
            continue
        if artist and _fold(artist) not in _fold(hit.get("artistName")):
            continue
        return lookup_album(hit["collectionId"])
    return None


def from_apple(title, ids=(), artist="", note=lambda _m: None):
    """Info for a favorite: by catalogue id if it has one, else by exact name.

    Returns (info, source) — source is "apple" for an id lookup, "search" for a
    name match, or None with info None when nothing trustworthy turned up.
    """
    found = apple_id(*ids)
    try:
        if found:
            kind, number = found
            note(f"apple {kind} id {number}")
            info = {"album": lookup_album, "song": lookup_song,
                    "playlist": lookup_playlist}[kind](number)
            if info:
                return info, "apple"
            note("not in this storefront")
        info = search_album(title, artist)
        if info:
            return info, "search"
        note("no exact match by name")
    except Exception as e:  # offline, or Apple changed something
        note(f"lookup failed: {e}")
    return None, None
