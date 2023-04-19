from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyAsoka.GUI.Widgets.AVideo import AVideo
from PyAsoka.src.Core.Signal import Signal


class Media:
    def __init__(self, _audio_=False):
        self._player_ = QMediaPlayer()
        self._audio_ = QAudioOutput()
        self._widget_ = None
        self._position_ = 0
        self._volume_ = 0

        self.position_changed = Signal(int)
        self.media_changed = Signal()

        self._player_.setAudioOutput(self._audio_)
        self._player_.positionChanged.connect(self.position_changed)

    def audio(self):
        return self._audio_

    def widget(self, parent=None):
        if self._widget_ is None:
            self._widget_ = AVideo(parent=parent)
            self._player_.setVideoOutput(self._widget_._video_)
            self._widget_.scrolled.connect(self.scrollVideo)
            self._widget_.volume_changed.bind(self.setVolume)
            self._widget_.played.bind(self.play)
            self._widget_.paused.bind(self.pause)
        return self._widget_

    def setSource(self, source):
        self._player_.setSource(source)

    def setVolume(self, value):
        self._volume_ = value
        self._audio_.setVolume(value / 100)

    def setPosition(self, position):
        self._position_ = position
        self._player_.setPosition(position)

    def scrollVideo(self, value):
        self.setPosition(self._player_.position() + value * 5000)

    def scrollVolume(self, value):
        self.setVolume(self._audio_.volume() * 100 + value * 5)

    def play(self):
        self._player_.play()
        print('played')

    def pause(self):
        self._player_.pause()
        print('paused')

    def stop(self):
        self._player_.stop()
