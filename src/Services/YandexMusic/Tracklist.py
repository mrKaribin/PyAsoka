from yandex_music.tracks_list import TracksList
from PyAsoka.src.Debug.Exceptions import Exceptions


class Tracklist:
    def __init__(self, tracks: TracksList):
        self._list_ = tracks

    @property
    def tracks(self):
        return self._list_.tracks

    def size(self):
        return len(self._list_.tracks)

    def __getitem__(self, item):
        from PyAsoka.src.Services.YandexMusic.Track import Track
        if isinstance(item, int):
            if 0 <= item < self.size():
                return Track(self._list_.tracks[item].fetchTrack())
            else:
                raise Exception(f'Недопустимый индекс трека {item}')
        elif isinstance(item, slice):
            if 0 <= item.start < self.size() and 0 <= item.stop < self.size():
                return [Track(track.fetchTrack()) for track in self._list_.tracks[item]]
            else:
                raise Exception(f'Недопустимый диапазон индексов трека {item.start}:{item.stop}')
        else:
            raise Exceptions.UnsupportableType()

    def getTrack(self, item):
        return self.__getitem__(item)
