from yandex_music.track.track import Track as YMTrack

from PyAsoka.src.Services.YandexMusic.Artist import Artist
from PyAsoka.src.Services.YandexMusic.Album import Album


class Track:
    def __init__(self, track: YMTrack):
        self.artists = [Artist(artist) for artist in track.artists]
        self.albums = [Album(album) for album in track.albums]
        self._track_ = track

    @property
    def id(self):
        return self._track_.id

    @property
    def name(self):
        return self._track_.title

    @property
    def available(self):
        return self._track_.available

    @property
    def duration(self):
        return self._track_.duration_ms / 1000

    def download(self, filename):
        self._track_.download(filename)

    def similarTracks(self):
        from PyAsoka.src.Services.YandexMusic.Account import account
        account = account()
        tracks = [Track(track) for track in account.client.tracks_similar(self.id).similar_tracks]
        return tracks

    def like(self):
        self._track_.like()

    def dislike(self):
        self._track_.dislike()
