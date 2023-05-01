from PyAsoka.src.GUI.Widget.Widget import Widget, Layer, Props, State, Styles, \
    QPainter, \
    QPaintEvent
from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.Graphics.Capture import Capture
from PyAsoka.Asoka import Asoka

from PySide6.QtGui import QPixmap, QImage

from threading import Thread
from enum import IntEnum

import cv2
import time


class VideoView(Widget):
    class State(IntEnum):
        STOP = 1
        PLAY = 2
        PAUSE = 3

    frameChanged = Signal(QImage)

    def __init__(self, video_path: str, cycle: bool = False, **kwargs):
        kwargs['style'] = Styles.Window
        super().__init__(**kwargs)
        self._video_path_ = video_path
        self._cycle_ = cycle
        self._frame_: QImage = None
        self._frame_alpha_: QImage = None
        self._video_state_: VideoView.State = VideoView.State.STOP

        self.layers.background.disable()
        self.layers.video.enable()

        self.frameChanged.connect(self.frameHandle, Asoka.ConnectionType.QueuedConnection)

        self._write_thread_ = Thread(target=self.writeThread)
        self._write_thread_.start()

    @property
    def frame(self):
        return self._frame_

    @property
    def videoState(self):
        return self._video_state_

    def play(self):
        self._video_state_ = VideoView.State.PLAY

    def stop(self):
        self._video_state_ = VideoView.State.STOP

    def pause(self):
        self._video_state_ = VideoView.State.PAUSE

    def frameHandle(self, frame):
        self._frame_ = frame
        self.repaint()

    def writeThread(self):
        State = VideoView.State
        while True:
            if self.videoState != State.STOP:
                capture = Capture(self._video_path_)
            while self.videoState != State.STOP:
                while (frame := capture.read()) is not False:
                    while self.videoState == VideoView.State.PAUSE:
                        time.sleep(Asoka.defaultCycleDelay)

                    if self.videoState == VideoView.State.STOP:
                        break

                    frame = frame.toRGB()()
                    h, w, ch = frame.shape
                    bytesPerLine = ch * w
                    image = QImage(frame, w, h, bytesPerLine, QImage.Format.Format_RGB888)
                    image = image.scaled(self.width(), self.height(), Asoka.AspectRatio.KeepAspectRatio,
                                         Asoka.TransformationMode.SmoothTransformation)
                    self.frameChanged.emit(image)
                    # self.runGuiTask(self.repaint)
                    del frame

                if not self._cycle_:
                    break
                else:
                    capture.setPosition(0)
            time.sleep(Asoka.defaultCycleDelay)

    class Video(Layer, level=Layer.Level.MIDDLE):
        def paint(self, widget, painter: QPainter, style, props: Props, event: QPaintEvent):
            if widget.frame is not None and widget.videoState != VideoView.State.STOP:
                painter.setOpacity(style.background.alpha())
                # if isinstance(widget.frame, QImage):
                # widget.frame.setAlphaChannel(widget._frame_alpha_)
                painter.drawPixmap(0, 0, widget.width(), widget.height(), QPixmap.fromImage(widget.frame))
                # print(style.background.alpha())
