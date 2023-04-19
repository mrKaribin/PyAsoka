from yandex_music.artist.artist import Artist as YMArtist


class Artist:
    def __init__(self, artist: YMArtist):
        self._artist_ = artist

    @property
    def id(self):
        return self._artist_.id

    @property
    def name(self):
        return self._artist_.name
