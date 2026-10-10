"""Logic tests for MusicBox, using fake speakers so no real Sonos is needed.

Stubs the `soco` module before importing the core, then drives the box through
the exact sequences the panel produces. Run:  python tests/test_core.py
"""

import os
import sys
import types

# --- stub the `soco` package so `import soco` works without it installed ----
_soco = types.ModuleType("soco")
_exc = types.ModuleType("soco.exceptions")


class SoCoException(Exception):
    pass


_exc.SoCoException = SoCoException
_soco.exceptions = _exc
_soco.discover = lambda timeout=None, **kw: set()
sys.modules["soco"] = _soco
sys.modules["soco.exceptions"] = _exc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicbox.core import MusicBox  # noqa: E402
from musicbox.feedback import Buzzer  # noqa: E402


class FakeFavorite:
    def __init__(self, title, item_class="object.item.audioItem.musicTrack"):
        self.title = title
        self.item_class = item_class
        self.resources = [types.SimpleNamespace(uri=f"uri:{title}")]
        self.resource_meta_data = f"meta:{title}"

    @property
    def reference(self):
        # soco parses the favorite's resMD into the object it points to; we just
        # mirror the class + resources so MusicBox can tell stream from container.
        return types.SimpleNamespace(item_class=self.item_class, resources=self.resources)


class FakePlaylist:
    """A Sonos playlist as soco returns it: the container itself, no .reference."""

    def __init__(self, title):
        self.title = title
        self.item_class = "object.container.playlistContainer"
        self.resources = [types.SimpleNamespace(uri=f"pl:{title}")]


class FakeLibrary:
    def __init__(self, favorites):
        self._favs = favorites

    def get_sonos_favorites(self):
        return self._favs


class FakeSpeaker:
    def __init__(self, name, favorites, playlists=()):
        self.player_name = name
        self.volume = 30
        self.play_mode = "NORMAL"
        self.music_library = FakeLibrary(favorites)
        self._playlists = list(playlists)
        self.transport_state = "STOPPED"
        self.log = []

    def get_sonos_playlists(self):
        return self._playlists

    def join(self, master):
        self.log.append(f"join:{master.player_name}")

    def unjoin(self):
        self.log.append("unjoin")

    def play_uri(self, uri, meta=None):
        self.log.append(f"play_uri:{uri}")
        self.transport_state = "PLAYING"

    def clear_queue(self):
        self.log.append("clear_queue")

    def add_to_queue(self, item, **kwargs):
        self.log.append(f"add_to_queue:{item.resources[0].uri}")
        return 1

    def play_from_queue(self, index, start=True):
        self.log.append(f"play_from_queue:{index}")
        self.transport_state = "PLAYING"

    def play(self):
        self.transport_state = "PLAYING"

    def pause(self):
        self.transport_state = "PAUSED_PLAYBACK"

    def stop(self):
        self.transport_state = "STOPPED"
        self.log.append("stop")

    def next(self):
        self.log.append("next")

    def previous(self):
        self.log.append("previous")

    def get_current_transport_info(self):
        return {"current_transport_state": self.transport_state}


class RecordingBuzzer(Buzzer):
    def __init__(self):
        self.cues = []

    def _emit(self, cue):
        self.cues.append(cue)


def make_box():
    favs = [FakeFavorite("Bohemian Rhapsody"), FakeFavorite("Discover Sonos Radio"),
            FakeFavorite("Greatest Hits", item_class="object.container.album.musicAlbum")]
    pls = [FakePlaylist("Saturday Kitchen")]
    box = MusicBox(card_map={"bohemian": "Bohemian Rhapsody"}, buzzer=RecordingBuzzer())
    box.speakers = {n: FakeSpeaker(n, favs, pls) for n in ("Alrum", "Køkken", "Grys værelse")}
    return box


def check_art_urls():
    from musicbox.core import bigger_art_urls

    # the shape Sonos actually hands out: the service's own url, already direct
    direct = ("https://is2-ssl.mzstatic.com/image/thumb/Music118/v4/eb/1f/12/"
              "eb1f12ec-474c-63aa-43af-09282f423b9d/00602537004737.rgb.jpg/"
              "400x400bb.jpeg")
    got = bigger_art_urls(direct)
    check("direct service url is upgraded", got and got[0].endswith(
        "00602537004737.rgb.jpg/1400x1400bb.jpeg"))
    check("the asset id is not mistaken for a size",
          "00602537004737.rgb.jpg" in got[0])
    check("sizes ladder down for a service that refuses the biggest",
          [u.rsplit("/", 1)[-1] for u in got] ==
          ["1400x1400bb.jpeg", "1200x1200bb.jpeg", "800x800bb.jpeg"])

    # ...and the proxied shape, with the service url in u=
    proxy = ("http://192.168.1.50:1400/getaa?s=1&u=https%3A%2F%2Fis1-ssl.mzstatic"
             ".com%2Fimage%2Fthumb%2FMusic%2Fab%2F400x400bb.jpg")
    check("proxied url is unwrapped and upgraded",
          bigger_art_urls(proxy)[0] ==
          "https://is1-ssl.mzstatic.com/image/thumb/Music/ab/1400x1400bb.jpg")
    check("already-large art left alone",
          bigger_art_urls(direct.replace("400x400", "1500x1500")) == [])
    check("non-http sources left alone",
          bigger_art_urls("http://x:1400/getaa?s=1&u=x-sonos-http%3Aa.mp3") == [])
    check("art url without a size left alone",
          bigger_art_urls("https://a.com/cover.jpg") == [])


class GoneSpeaker(FakeSpeaker):
    """A speaker the box still holds, at an address it has since lost."""

    def _gone(self, *a, **k):
        raise ConnectionError("[Errno 113] No route to host")

    play_uri = clear_queue = stop = next = get_current_transport_info = _gone


def check_self_healing():
    import musicbox.core as core

    def rediscover_as(speakers):
        core.soco.discover = lambda timeout=None, **kw: set(speakers)

    # a speaker that moved address: the card's first try fails on the network,
    # the box finds the speakers again and plays on the fresh one — no error
    box = make_box()
    favs = box.speakers["Køkken"].music_library._favs
    box.speakers["Køkken"] = GoneSpeaker("Køkken", favs)
    fresh = FakeSpeaker("Køkken", favs)
    rediscover_as([fresh, box.speakers["Alrum"]])
    box.toggle_room("Køkken")
    box.place_card("bohemian")
    r = box.play()
    check("a moved speaker is found again and plays", r["ok"]
          and any("play_uri" in e for e in fresh.log))
    check("no error beep for a healed play", "error" not in box.buzzer.cues)
    check("the speaker list now holds the fresh one", box.speakers["Køkken"] is fresh)

    # pause/resume and skip heal the same way
    box.speakers["Køkken"] = GoneSpeaker("Køkken", favs)
    check("pause heals a moved speaker", box.play()["message"] == "Paused")
    box.speakers["Køkken"] = GoneSpeaker("Køkken", favs)
    check("next heals a moved speaker", box.next()["ok"] and "next" in fresh.log)

    # removing the card still stops the music after a move
    box.play()  # resume
    box.speakers["Køkken"] = GoneSpeaker("Køkken", favs)
    box.remove_card()
    check("removal stops a moved speaker", fresh.log[-1] == "stop")

    # an armed room missing from the list (it was off at the last search)
    box = make_box()
    box.toggle_room("Køkken")
    kok = box.speakers.pop("Køkken")
    rediscover_as(list(box.speakers.values()) + [kok])
    box.place_card("bohemian")
    check("an armed room missing from the list is searched for",
          box.play()["ok"] and any("play_uri" in e for e in kok.log))

    # the Sonos app grouped the room under another: only coordinators take play_uri
    box = make_box()
    kok = box.speakers["Køkken"]
    calls = []
    def refuse_once(uri, meta=None):
        calls.append(uri)
        if len(calls) == 1:
            raise core.SoCoException("not the coordinator")
        FakeSpeaker.play_uri(kok, uri, meta)
    kok.play_uri = refuse_once
    rediscover_as(box.speakers.values())
    box.toggle_room("Køkken")
    box.place_card("bohemian")
    r = box.play()
    check("a regrouped room is made its own coordinator and plays",
          r["ok"] and "unjoin" in kok.log and len(calls) == 2)

    # nobody answers at all: one error, and a speaker list left intact
    box = make_box()
    favs = box.speakers["Køkken"].music_library._favs
    box.speakers["Køkken"] = GoneSpeaker("Køkken", favs)
    rediscover_as([])
    box.toggle_room("Køkken")
    box.place_card("bohemian")
    r = box.play()
    check("an unreachable speaker errors once, not crashes",
          not r["ok"] and box.buzzer.cues[-1] == "error")
    check("a failed search keeps the old speakers", "Alrum" in box.speakers)

    # shuffle latched in before the card goes down applies to that card
    box = make_box()
    box.set_shuffle(True)
    box.toggle_room("Køkken")
    box.place_card("bohemian")
    box.play()
    check("a latched shuffle applies to a fresh card",
          box.speakers["Køkken"].play_mode == "SHUFFLE_NOREPEAT")

    core.soco.discover = lambda timeout=None, **kw: set()


def check_album_info():
    from musicbox import albuminfo

    # a Sonos playlist is read off the speakers, no catalogue needed
    box = make_box()
    for spk in box.speakers.values():
        spk.music_library.browse = lambda item, max_items=100: [
            types.SimpleNamespace(title="Spor 1", creator="Kim Larsen"),
            types.SimpleNamespace(title="Spor 2", creator="Kim Larsen")]
    info = box.info_for("Saturday Kitchen")
    check("a playlist's tracks come from Sonos", info["tracks"] == ["Spor 1", "Spor 2"]
          and info["source"] == "sonos" and info["artist"] == "Kim Larsen")

    # an Apple Music album favorite is looked up by the id in its metadata
    asked = []
    def fake_get(path, **params):
        asked.append((path, params))
        return [{"wrapperType": "collection", "artistName": "Sigurd Barrett",
                 "collectionName": "Kongen Af Danmark - EP"},
                {"wrapperType": "track", "kind": "song", "trackName": "To", "trackNumber": 2},
                {"wrapperType": "track", "kind": "music-video", "trackName": "Video"},
                {"wrapperType": "track", "kind": "song", "trackName": "En", "trackNumber": 1}]
    real_get, albuminfo._get = albuminfo._get, fake_get
    try:
        box = make_box()
        fav = box.speakers["Alrum"].music_library._favs[2]   # Greatest Hits, an album
        fav.resources = [types.SimpleNamespace(
            uri="x-rincon-cpcontainer:1004206calbum%3a1440857781?sid=204")]
        info = box.info_for("Greatest Hits")
        check("an Apple album is looked up by its catalogue id",
              asked[0][0] == "lookup" and asked[0][1]["id"] == "1440857781")
        check("its tracks come back in order, without the videos",
              info["tracks"] == ["En", "To"] and info["source"] == "apple")
        check("the ' - EP' is dropped from the album name",
              info["album"] == "Kongen Af Danmark" and info["artist"] == "Sigurd Barrett")

        albuminfo._get = lambda path, **params: (_ for _ in ()).throw(OSError("offline"))
        info = box.info_for("Greatest Hits")
        check("offline, the label still gets the title to edit",
              info["album"] == "Greatest Hits" and info["tracks"] == [] and info["source"] == "")
    finally:
        albuminfo._get = real_get

    # an Apple Music playlist's tracks come from its public page
    check("a playlist id is recognised",
          albuminfo.apple_id("1006206cplaylist%3Apl.b8336374491445a6") == ("playlist", "pl.b8336374491445a6"))
    check("a playlist id without pl. is not",
          albuminfo.apple_id("1006206cplaylist%3A12345") is None)
    page = """<html><script type="application/ld+json">{"@type": "MusicPlaylist",
      "name": "David Byrne Essentials", "track": [{"name": "Angels"},
      {"name": "Once In a Lifetime"}, {"name": "Strange Overtones"}]}</script>
      <script type="application/json" id="serialized-server-data">{"data": [{"items": [
      {"title": "Angels", "artistName": "David Byrne"},
      {"title": "Once In a Lifetime", "artistName": "Talking Heads"},
      {"title": "Strange Overtones", "artistName": "David Byrne & Brian Eno"}]}]}</script></html>"""
    real_page, albuminfo._page = albuminfo._page, lambda path: page
    try:
        box = make_box()
        fav = box.speakers["Alrum"].music_library._favs[2]
        fav.resources = [types.SimpleNamespace(
            uri="x-rincon-cpcontainer:1006206cplaylist%3Apl.b8336374491445a6?sid=204")]
        info = box.info_for("Greatest Hits")
        check("an Apple playlist gets its name and tracks from the page",
              info["album"] == "David Byrne Essentials" and info["source"] == "apple"
              and info["tracks"] == ["Angels", "Once In a Lifetime", "Strange Overtones"])
        check("its lead artist counts the duets", info["artist"] == "David Byrne")
    finally:
        albuminfo._page = real_page

    # a mix has no artist line, and says who sings each track instead
    artist, lines = albuminfo.tracklist([("Bien", "Lille Bille & Maria Lucia"),
                                         ("Rotten", "Lille Bille & Pharfar"),
                                         ("Fætter Mikkel", "Lars Stryg Band")])
    check("collaborations count for the lead artist", artist == "Lille Bille" and lines[0] == "Bien")
    artist, lines = albuminfo.tracklist([("A", "One"), ("B", "Two"), ("C", "Three")])
    check("a mix gets no artist, and each track its own",
          artist == "" and lines == ["A \u2013 One", "B \u2013 Two", "C \u2013 Three"])


def check(label, cond):
    if not cond:
        raise AssertionError(f"FAILED: {label}")
    print(f"  ok: {label}")


def main():
    # play with no room armed -> error beep, no-op
    box = make_box()
    r = box.play()
    check("no-room play is rejected", not r["ok"])
    check("no-room play beeps error", box.buzzer.cues == ["error"])

    # arm by fuzzy name
    box = make_box()
    check("fuzzy arm 'kok' resolves Køkken", box.toggle_room("kok")["ok"])
    check("Køkken is armed", "Køkken" in box.armed)
    check("arm fired arm cue", box.buzzer.cues[-1] == "arm")

    # unknown card -> error, no card on spot
    check("unknown card rejected", not box.place_card("nope")["ok"])
    check("no card on spot after bad card", box.current_card is None)

    # good card -> chirp
    check("known card accepted", box.place_card("bohemian")["ok"])
    check("card chirps", box.buzzer.cues[-1] == "card")

    # play with armed room + card -> plays favorite on coordinator
    r = box.play()
    check("play succeeds", r["ok"])
    check("coordinator is Køkken", box.coordinator_name == "Køkken")
    check("Køkken got play_uri", any("play_uri" in e for e in box.speakers["Køkken"].log))
    check("playing flag set", box.playing is True)

    # arm a second room while playing -> joins live
    box.toggle_room("Alrum")
    check("Alrum joined coordinator live", any("join:Køkken" in e for e in box.speakers["Alrum"].log))

    # volume: absolute and relative, clamped
    check("absolute volume set", box.set_volume("Alrum", 80)["ok"])
    check("Alrum volume is 80", box.speakers["Alrum"].volume == 80)
    box.nudge_volume("Alrum", "+50")
    check("relative volume clamps at 100", box.speakers["Alrum"].volume == 100)

    # shuffle+repeat -> SHUFFLE play_mode applied to coordinator
    box.set_shuffle(True)
    box.set_repeat(True)
    check("play_mode is SHUFFLE", box.speakers["Køkken"].play_mode == "SHUFFLE")

    # next works while playing
    check("next succeeds", box.next()["ok"])
    check("coordinator got next", "next" in box.speakers["Køkken"].log)

    # disarm coordinator's partner stops it live
    box.toggle_room("Alrum")
    check("Alrum unjoined live", "unjoin" in box.speakers["Alrum"].log)

    # removing the card off the spot stops playback (physical behaviour)
    box.remove_card()
    check("removing card stops coordinator", "stop" in box.speakers["Køkken"].log)
    check("not playing after card removed", box.playing is False)

    # play with armed room but no card -> pause/resume toggle
    box2 = make_box()
    box2.toggle_room("Alrum")
    box2.speakers["Alrum"].transport_state = "PLAYING"
    r = box2.play()
    check("no-card play pauses when playing", r["message"] == "Paused")

    # card on the spot: first play loads the favorite, further presses are
    # pause/resume — they must NOT restart the favorite (turntable behaviour)
    box3 = make_box()
    box3.toggle_room("Køkken")
    box3.place_card("bohemian")
    box3.play()  # initial: loads the favorite
    plays_after_start = sum("play_uri" in e for e in box3.speakers["Køkken"].log)
    r = box3.play()  # second press while card still on spot
    check("second play pauses, not restarts", r["message"] == "Paused")
    check("second play did not re-issue play_uri",
          sum("play_uri" in e for e in box3.speakers["Køkken"].log) == plays_after_start)
    r = box3.play()  # third press resumes
    check("third play resumes", r["message"] == "Resumed")
    check("no extra play_uri on resume",
          sum("play_uri" in e for e in box3.speakers["Køkken"].log) == plays_after_start)

    # album/playlist favorites are containers: must be queued, not play_uri'd
    # (play_uri on a container is the UPnP 714 "Illegal MIME-Type" bug)
    boxA = make_box()
    boxA.card_map["album"] = "Greatest Hits"
    boxA.toggle_room("Køkken")
    boxA.place_card("album")
    r = boxA.play()
    log = boxA.speakers["Køkken"].log
    check("album play succeeds", r["ok"])
    check("album cleared the queue first", "clear_queue" in log)
    check("album added to the queue", any(e.startswith("add_to_queue:") for e in log))
    check("album played from the queue", "play_from_queue:0" in log)
    check("album did NOT use play_uri", not any("play_uri" in e for e in log))
    # Sonos playlists are bindable too, and are containers like an album — but
    # without the favorite's .reference wrapper, so the queue path must take the
    # item itself
    boxP = make_box()
    check("playlists are offered alongside favorites",
          "Saturday Kitchen" in boxP.playlist_titles()
          and "Saturday Kitchen" not in boxP.favorite_titles())
    boxP.card_map["party"] = "Saturday Kitchen"
    boxP.toggle_room("Køkken")
    boxP.place_card("party")
    r = boxP.play()
    plog = boxP.speakers["Køkken"].log
    check("playlist play succeeds", r["ok"])
    check("playlist queued, not streamed",
          "clear_queue" in plog and "add_to_queue:pl:Saturday Kitchen" in plog
          and "play_from_queue:0" in plog and not any("play_uri" in e for e in plog))

    # queued album means prev/next navigate its tracks on the coordinator
    check("next works on a queued album", boxA.next()["ok"])
    check("coordinator got next", "next" in log)
    check("previous works on a queued album", boxA.previous()["ok"])
    check("coordinator got previous", "previous" in log)

    # a track favorite still goes straight to play_uri (no queue churn)
    boxT = make_box()
    boxT.toggle_room("Køkken")
    boxT.place_card("bohemian")
    boxT.play()
    logT = boxT.speakers["Køkken"].log
    check("track used play_uri", any("play_uri" in e for e in logT))
    check("track did not touch the queue", not any("queue" in e for e in logT))

    check_art_urls()
    check_self_healing()
    check_album_info()

    print("\nAll core-logic checks passed.")


if __name__ == "__main__":
    main()
