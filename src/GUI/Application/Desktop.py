from PyAsoka.src.GUI.Widget.Widget import Widget, Layer, QPainter, QPaintEvent, Props, Color, QBrush, QPoint
from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.src.GUI.API.API import API
from PyAsoka.Asoka import Asoka

from PySide6.QtGui import QPixmap, QImage, QLinearGradient


class Desktop(Widget):
    def __init__(self, manager: 'ScreenManager', screen: API.Screen):
        super().__init__(style=Styles.Desktop, geometry=screen.geometry)
        self._manager_ = manager
        self._screen_ = screen
        self._sleep_frame_: QImage = None

        self.geometry = screen.geometry
        self.layers.overlay.alphaChanged.connect(self.repaint)

    @property
    def manager(self):
        return self._manager_

    @property
    def sleepFrame(self):
        return self._sleep_frame_

    def __sleep_frame_handle__(self, frame: QImage):
        self._sleep_frame_ = frame
        self.repaint()

    class Background(Layer, level=Layer.Level.MIDDLE):
        def paint(self, widget, painter: QPainter, style, props: Props, event: QPaintEvent):
            pass

    class Overlay(Layer, level=Layer.Level.MIDDLE):
        def paint(self, widget, painter: QPainter, style, props: Props, event: QPaintEvent):
            length = 0.25
            col = 30
            painter.setPen(Color(0, 0, 0, 0))
            painter.setOpacity(self.alpha)

            grad = QLinearGradient(QPoint(0, 0), QPoint(widget.width(), 0))
            grad.setColorAt(0.0, Color(col, col, col, 220))
            grad.setColorAt(length, Color(0, 0, 0, 0))
            grad.setColorAt(1.0 - length, Color(0, 0, 0, 0))
            grad.setColorAt(1.0, Color(col, col, col, 220))
            painter.setBrush(QBrush(grad))
            painter.drawRect(0, 0, int(widget.width() * length), widget.height())
            painter.drawRect(widget.width() - int(widget.width() * length), 0, widget.width(), widget.height())

    class Video(Layer, level=Layer.Level.MIDDLE):
        def paint(self, widget, painter: QPainter, style, props: Props, event: QPaintEvent):
            if widget.sleepFrame is not None:
                painter.setOpacity(self.alpha)
                painter.drawPixmap(0, 0, widget.width(), widget.height(), QPixmap.fromImage(widget.sleepFrame))
