from PyAsoka.GUI.Widgets.AWidget import *

from PySide6.QtGui import QMovie


class AGifAnimation(AWidget):
    def __init__(self, filename, speed: int = None, looped: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # public
        self.gif = QMovie(filename)
        self.speed = speed if speed is not None else self.gif.speed()
        self.looped = looped

        # signals
        self.ended = ASignal(AGifAnimation)

        # prepare
        self.gif.start()
        self.gif.setBackgroundColor(QColor(0, 0, 0, 0))

        self.gif.updated.connect(self.repaint)
        if not looped:
            self.gif.finished.connect(lambda: self.ended(self))

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        image = self.gif.currentPixmap()
        painter.setOpacity(self.alpha)
        painter.drawPixmap(0, 0, self.width(), self.height(), image, 0, 0, image.width(), image.height())
