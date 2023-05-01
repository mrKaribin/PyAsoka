from PyAsoka.src.GUI.Widget.Widget import Widget, Layer, QPainter, QPaintEvent, Props
from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.src.GUI.API.API import API
from PyAsoka.Asoka import Asoka

from PySide6.QtGui import QPixmap, QImage


class Desktop(Widget):
    def __init__(self, manager: 'ScreenManager', screen: API.Screen):
        super().__init__(style=Styles.Desktop, geometry=screen.geometry)
        self._manager_ = manager
        self._screen_ = screen
        self._sleep_frame_: QImage = None

        self.geometry = screen.geometry

    @property
    def manager(self):
        return self._manager_

    @property
    def sleepFrame(self):
        return self._sleep_frame_

    def __sleep_frame_handle__(self, frame: QImage):
        self._sleep_frame_ = frame
        self.repaint()

    class Video(Layer, level=Layer.Level.MIDDLE):
        def paint(self, widget, painter: QPainter, style, props: Props, event: QPaintEvent):
            if widget.sleepFrame is not None:
                painter.setOpacity(self.alpha)
                painter.drawPixmap(0, 0, widget.width(), widget.height(), QPixmap.fromImage(widget.sleepFrame))
