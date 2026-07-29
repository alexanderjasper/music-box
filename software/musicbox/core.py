"""MusicBox core — all the Sonos logic, no hardware and no UI.

This is the brain. The CLI and the web UI are just two different sets of
"buttons" wired to the same methods here; on the Pi, real GPIO buttons will be a
third. Keeping this layer hardware- and UI-agnostic is what lets us validate the
whole behaviour on a laptop today and move it onto the device unchanged.

Every action returns a small result dict ({"ok": bool, "message": str}) and, as a
side effect, fires the appropriate buzzer cue — exactly as the real box will.
"""

import soco
from soco.exceptions import SoCoException

from .feedback import SilentBuzzer

# (shuffle, repeat) -> Sonos play_mode string
PLAY_MODES = {
    (False, False): "NORMAL",
    (False, True): "REPEAT_ALL",
    (True, False): "SHUFFLE_NOREPEAT",
    (True, True): "SHUFFLE",  # Sonos "SHUFFLE" means shuffle + repeat all
}


def _clamp(v):
    return max(0, min(100, int(v)))


# Fold Danish/diacritic letters so "kok" matches "Køkken" at a keyboard.
_FOLD = str.maketrans({"ø": "o", "æ": "a", "å": "a", "ö": "o", "ä": "a", "é": "e"})


def _norm(s):
    return s.strip().lower().translate(_FOLD)


class MusicBox:
    def __init__(self, card_map=None, buzzer=None):
        self.buzzer = buzzer or SilentBuzzer()
        self.card_map = dict(card_map or {})  # card id -> favorite/playlist query
        self.speakers = {}                     # room name -> SoCo device
        self.armed = set()                     # armed room names
        self.shuffle = False
        self.repeat = False
        self.current_card = None               # the card on the spot, or None
        self._card_started = False             # has this card's favorite been loaded+started?
        self.playing = False
        self.coordinator_name = None
        self._fav_cache = None
        self._playlist_cache = None

    # --- setup -----------------------------------------------------------

    def discover(self):
        found = soco.discover(timeout=10)
        if not found:
            raise RuntimeError(
                "No Sonos speakers found. Same Wi-Fi as the speakers? "
                "Firewall blocking UDP 1900?"
            )
        self.speakers = {s.player_name: s for s in found}
        return self.rooms()

    def rooms(self):
        return sorted(self.speakers)

    # --- room arming (encoder push) -------------------------------------

    def toggle_room(self, query):
        name = self._resolve_room(query)
        if not name:
            self.buzzer.error()
            return _err(f"No single room matches {query!r}.")
        if name in self.armed:
            self.armed.discard(name)
            self.buzzer.disarmed()
            if self.playing:  # live: leaving the group stops this room now
                self._try(self.speakers[name].unjoin)
            return _ok(f"{name} disarmed")
        self.armed.add(name)
        self.buzzer.armed()
        if self.playing and self.coordinator_name and name != self.coordinator_name:
            # live: arming while music plays joins this room into the group now
            self._try(lambda: self.speakers[name].join(self.speakers[self.coordinator_name]))
        return _ok(f"{name} armed")

    # --- volume (encoder turn) ------------------------------------------

    def nudge_volume(self, query, delta):
        return self._set_volume(query, relative=int(delta))

    def set_volume(self, query, level):
        return self._set_volume(query, absolute=_clamp(level))

    def _set_volume(self, query, absolute=None, relative=None):
        name = self._resolve_room(query)
        if not name:
            self.buzzer.error()
            return _err(f"No single room matches {query!r}.")
        spk = self.speakers[name]
        try:
            level = absolute if absolute is not None else _clamp(spk.volume + relative)
            spk.volume = level
        except SoCoException as e:
            self.buzzer.error()
            return _err(f"Sonos error setting volume: {e}")
        return _ok(f"{name} volume = {level}")

    # --- mode toggles ----------------------------------------------------

    def set_shuffle(self, on):
        self.shuffle = bool(on)
        self.buzzer.mode_changed()
        self._reapply_play_mode()
        return _ok(f"shuffle {'on' if self.shuffle else 'off'}")

    def set_repeat(self, on):
        self.repeat = bool(on)
        self.buzzer.mode_changed()
        self._reapply_play_mode()
        return _ok(f"repeat {'on' if self.repeat else 'off'}")

    # --- card spot -------------------------------------------------------

    def place_card(self, card_id):
        card_id = str(card_id).strip()
        if card_id not in self.card_map:
            self.current_card = None
            self.buzzer.error()
            return _err(f"Unknown card {card_id!r} (not in card map).")
        self.current_card = card_id
        self._card_started = False  # a fresh card: the next play loads its favorite
        self.buzzer.card_recognized()
        return _ok(f"card {card_id!r} -> favorite {self.card_map[card_id]!r}")

    def remove_card(self):
        # Physical behaviour: lifting the card off the spot stops the music.
        self.current_card = None
        self._card_started = False
        if self.playing and self.coordinator_name:
            self._try(self.speakers[self.coordinator_name].stop)
        self.playing = False
        return _ok("card removed — playback stopped")

    # --- transport -------------------------------------------------------

    def play(self):
        if not self.armed:
            self.buzzer.error()  # the deliberate no-op: error beep, nothing else
            return _err("No room armed — error beep, nothing happens.")
        coordinator = self._group_armed()

        # A freshly placed card we haven't started yet: load and play its
        # favorite. Once started, the card stays on the spot (turntable
        # behaviour) so further play presses must NOT reload it — they fall
        # through to pause/resume below, same as the no-card case.
        if self.current_card and not self._card_started:
            query = self.card_map[self.current_card]
            fav = self._find_playable(query)
            if not fav:
                self.buzzer.error()
                return _err(f"No Sonos favorite or playlist matches {query!r}.")
            try:
                self._start_item(coordinator, fav)
            except SoCoException as e:
                self.buzzer.error()
                return _err(f"Sonos refused to play: {e}")
            self._reapply_play_mode()
            self.playing = True
            self._card_started = True
            self.buzzer.confirm()
            return _ok(f"Playing {fav.title!r} in {', '.join(sorted(self.armed))}")

        # Card already started, or no card on the spot: play acts as
        # pause/resume on the current group.
        try:
            state = coordinator.get_current_transport_info()["current_transport_state"]
            if state == "PLAYING":
                coordinator.pause()
                self.playing = False
                return _ok("Paused")
            coordinator.play()
            self.playing = True
            self.buzzer.confirm()
            return _ok("Resumed")
        except SoCoException as e:
            self.buzzer.error()
            return _err(f"Nothing to resume: {e}")

    def next(self):
        return self._skip("next")

    def previous(self):
        return self._skip("previous")

    def _skip(self, action):
        if not self.coordinator_name:
            self.buzzer.error()
            return _err("Nothing playing.")
        try:
            getattr(self.speakers[self.coordinator_name], action)()
            return _ok(action)
        except SoCoException:
            self.buzzer.error()
            return _err(f"Can't {action} this source (e.g. a single track or radio).")

    # --- snapshot for UIs ------------------------------------------------

    def state(self, with_volumes=True):
        volumes = {}
        if with_volumes:
            for name, spk in self.speakers.items():
                try:
                    volumes[name] = spk.volume
                except SoCoException:
                    volumes[name] = None
        return {
            "rooms": self.rooms(),
            "armed": sorted(self.armed),
            "volumes": volumes,
            "shuffle": self.shuffle,
            "repeat": self.repeat,
            "current_card": self.current_card,
            "card_target": self.card_map.get(self.current_card),
            "playing": self.playing,
            "cards": self.card_map,
        }

    # --- internals -------------------------------------------------------

    def _resolve_room(self, query):
        q = _norm(str(query))
        for name in self.speakers:
            if _norm(name) == q:
                return name
        matches = [n for n in self.speakers if q and q in _norm(n)]
        return matches[0] if len(matches) == 1 else None

    def _favorites(self, refresh=False):
        if self._fav_cache is None or refresh:
            if not self.speakers:
                return []
            any_speaker = next(iter(self.speakers.values()))
            self._fav_cache = list(any_speaker.music_library.get_sonos_favorites())
        return self._fav_cache

    def favorite_titles(self, refresh=False):
        """The live Sonos Favorite titles — what the config UI lists to bind cards to."""
        return [fav.title for fav in self._favorites(refresh=refresh)]

    def _playlists(self, refresh=False):
        """Sonos playlists — saved queues, which are *not* in the favorites list."""
        if self._playlist_cache is None or refresh:
            if not self.speakers:
                return []
            any_speaker = next(iter(self.speakers.values()))
            try:
                self._playlist_cache = list(any_speaker.get_sonos_playlists())
            except Exception:
                self._playlist_cache = []   # older soco, or a fake speaker
        return self._playlist_cache

    def playlist_titles(self, refresh=False):
        """The live Sonos playlist titles, also bindable to a card."""
        return [pl.title for pl in self._playlists(refresh=refresh)]

    def _start_item(self, coordinator, item):
        """Begin playback of a favorite or a Sonos playlist, whichever it is.

        A favorite points either to a single, directly-playable stream (a track
        or a radio station) or to a *container* — an album, playlist or artist. A
        Sonos playlist is always a container, and is itself the item rather than a
        wrapper around one. Only a stream can be handed to play_uri /
        SetAVTransportURI; doing that with a container makes Sonos reject it with
        UPnP 714 "Illegal MIME-Type". Containers have to be loaded into the queue
        and played from there, which is also what lets shuffle/repeat span them.
        """
        target = self._container_target(item)
        if target is not None:
            coordinator.clear_queue()
            coordinator.add_to_queue(target)
            coordinator.play_from_queue(0)
        else:
            coordinator.play_uri(item.resources[0].uri, meta=item.resource_meta_data)

    @staticmethod
    def _container_target(item):
        """What to load into the queue, or None if the item should be streamed.

        Favorites wrap the thing they point at in `.reference`; a Sonos playlist
        *is* the thing.
        """
        target = getattr(item, "reference", item)
        try:
            return target if target.item_class.startswith("object.container") else None
        except Exception:
            return None  # unparseable metadata: treat as a stream, try play_uri

    def artwork_for(self, query):
        """Album-art bytes for the favorite or playlist matching query, or None.

        Sonos serves the art itself, so this only works on the LAN — which is
        where the label page runs.
        """
        import urllib.request

        item = self._find_playable(query)
        if item is None or not self.speakers:
            return None
        uri = (getattr(item, "album_art_uri", None)
               or getattr(getattr(item, "reference", None), "album_art_uri", None))
        if not uri:
            return None
        speaker = next(iter(self.speakers.values()))
        full = speaker.music_library.build_album_art_full_uri(uri)
        with urllib.request.urlopen(full, timeout=6) as r:
            return r.read()

    def _find_playable(self, query):
        """Match a favorite or Sonos playlist by title substring.

        Both lists are cached, so something added in the Sonos app after the box
        started would otherwise stay invisible until a restart. A miss is rare and
        cheap, so it costs one refresh rather than a stale error beep. Favorites
        win over playlists of the same name.
        """
        q = query.lower()
        for refresh in (False, True):
            for item in self._favorites(refresh=refresh) + self._playlists(refresh=refresh):
                if q in item.title.lower():
                    return item
        return None

    def _group_armed(self):
        names = sorted(self.armed)
        coordinator = self.speakers[names[0]]
        self.coordinator_name = names[0]
        for n in names[1:]:
            self._try(lambda spk=self.speakers[n]: spk.join(coordinator))
        return coordinator

    def _reapply_play_mode(self):
        if self.playing and self.coordinator_name:
            mode = PLAY_MODES[(self.shuffle, self.repeat)]
            self._try(lambda: setattr(self.speakers[self.coordinator_name], "play_mode", mode))

    @staticmethod
    def _try(fn):
        try:
            fn()
        except SoCoException:
            pass


def _ok(message):
    return {"ok": True, "message": message}


def _err(message):
    return {"ok": False, "message": message}
