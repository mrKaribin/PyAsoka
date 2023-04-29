from PyAsoka.src.GUI.Widget.Widget import Widget, Styles, QPaintEvent, QPoint, QSize, QRect, QPainter, QPen, QBrush, \
    Color, QResizeEvent
from PyAsoka.src.GUI.Widgets.AIconView import AIconView
from PyAsoka.src.GUI.Widgets.TextView import TextView
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.Asoka import Asoka

from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QWheelEvent


class VideoPanel(Widget):
    def __init__(self, position=0, volume=0, **kwargs):
        super(VideoPanel, self).__init__(style=Styles._widget_(), **kwargs)

        self.enabled = False
        self.playing = True
        self.enabled_height = 50
        self.volume = volume
        self.position = position
        self.pause = AIconView(Asoka.Project.Path.Asoka.Media.Images() + '\\pause.png', parent=self, clickable=True)
        self.vol = TextView(f'{self.volume}%', parent=self)

        self.pause.setFixedSize(30, 30)
        self.vol.setFixedSize(50, 50)

        self.pause.clicked.bind(self.pause_clicked)
        self.volume_changed = Signal(int)
        self.paused = Signal()
        self.played = Signal()

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.__set_volume__(self.volume + event.pixelDelta().y() // 120 * 5)
        self.volume_changed(self.volume)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super(VideoPanel, self).resizeEvent(event)
        self.pause.move(QPoint((self.width() - self.pause.width()) // 2, (self.height() - self.pause.height()) // 2))
        self.vol.move(QPoint(self.width() - self.pause.width() - 10, (self.height() - self.pause.height()) // 2))

    def __set_volume__(self, value):
        self.volume = value
        self.vol.setText(f'{self.volume}%')

    def pause_clicked(self):
        self.playing = not self.playing
        if self.playing:
            self.played()
            self.pause.setImage(a.dir.images() + '/pause.png')
            self.update()
        else:
            self.paused()
            self.pause.setImage(a.dir.images() + '/play.png')
            self.update()


class Video(QVideoWidget):
    def __init__(self, *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)

        self.scrolled = Signal(int)

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.scrolled(event.pixelDelta().y() // 120)


class AVideo(AWidget):
    def __init__(self, position=0, volume=0, **kwargs):
        super(AVideo, self).__init__(style=Styles.focusWidget(), **kwargs)

        self._video_ = Video(parent=self)
        self._panel_ = VideoPanel(position, volume, parent=self)

        self._video_.move(self._round_size_ // 2, self._round_size_ // 2)
        self._panel_.setGeometry(QRect(QPoint(0, self.height()), QSize(self.width(), 0)))
        self._panel_.hide(None)

        self.scrolled = self._video_.scrolled
        self.volume_changed = self._panel_.volume_changed
        self.played = self._panel_.played
        self.paused = self._panel_.paused

        self.resized.bind(self.__resize_video__)
        self._panel_.resized.bind(self.__resize_video__)
        # self._video_.scrolled.bind(self.scrolled)

    def __resize_video__(self):
        # self._video_.setGeometry(100, 100, 300, 300)
        self._video_.resize(self.width() - self._round_size_, self.height() - self._round_size_ - self._panel_.height())

    def paintEvent(self, event: QPaintEvent):
        indent, radius = int(self._frame_size_ * 1.5), self._round_size_
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(self.colors.frame, self._frame_size_))
        painter.setBrush(QBrush(Color(0, 0, 0, 255)))
        painter.drawRoundedRect(QRect(
            QPoint(indent, indent),
            QSize(self.size().width() - indent * 2, self.size().height() - indent * 2)
        ), self._round_size_, self._round_size_)

    def enterEvent(self, event):
        self._panel_._animations_geometry_.clear()
        anim = self._panel_.setGeometry(QRect(QPoint(0, self.height() - self._panel_.enabled_height),
                                              QSize(self.width(), self._panel_.enabled_height)), duration=100)
        anim.ended.bind(lambda: self._panel_.show())

    def leaveEvent(self, event):
        self._panel_._animations_geometry_.clear()
        anim = self._panel_.hide(100)
        self._panel_.setGeometry(QRect(QPoint(0, self.height()), QSize(self.width(), 0)), duration=100)
