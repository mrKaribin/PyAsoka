from yandex_music.playlist.playlist import Playlist as YMPlaylist


class Playlist:
    def __init__(self, playlist: YMPlaylist):
        self._playlist_ = playlist

    @property
    def name(self):
        return self._playlist_.title

    @property
    def tracksCount(self):
        return self._playlist_.track_count

    def getTrack(self, index):
        if 0 <= index < self.tracksCount:
            from PyAsoka.src.Services.YandexMusic.Track import Track
            return Track(self._playlist_.tracks[index].fetchTrack())
        else:
            raise Exception('Индекс трека вне допустимого диапазона')
