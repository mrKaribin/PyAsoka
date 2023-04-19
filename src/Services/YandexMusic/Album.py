from yandex_music.album.album import Album as YMAlbum


class Album:
    def __init__(self, album: YMAlbum):
        self._album_ = album

    @property
    def id(self):
        return self._album_.id

    @property
    def name(self):
        return self._album_.title

    @property
    def trackCount(self):
        return self._album_.track_count
