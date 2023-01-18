from PyAsoka.src.GUI.Widget.AnimationManager import Animation
from PyAsoka.src.Debug.Exceptions import Exceptions
from PySide6.QtCore import QPoint, QRect, QSize


class Animate:
    def __init__(self, widget):
        self._widget_ = widget

    def size(self, end_size: tuple | QSize, start_size: tuple | QSize = None, duration: int = 1000):
        if start_size is None:
            start_size = self._widget_.size()

        if isinstance(start_size, tuple) and len(start_size) == 2:
            start_size = QSize(*start_size)
        elif isinstance(start_size, QSize):
            start_size = start_size
        else:
            raise Exceptions.UnsupportableType(start_size)

        if isinstance(end_size, tuple) and len(end_size) == 2:
            end_size = QSize(*end_size)
        elif isinstance(end_size, QSize):
            end_size = end_size
        else:
            raise Exceptions.UnsupportableType(end_size)

        start_geom = QRect(self._widget_.position(), start_size)
        end_geom = QRect(self._widget_.position(), end_size)
        animation = Animation(self._widget_, b'geometry', start_geom, end_geom, duration)
        self._widget_.animations.start(animation)
        return animation

    def position(self, end_position: tuple | QPoint, start_position: tuple | QPoint, duration: int = 1000):
        if start_position is None:
            start_position = self._widget_.position()

        if isinstance(start_position, tuple) and len(start_position) == 2:
            start_position = QSize(*start_position)
        elif isinstance(start_position, QSize):
            start_position = start_position
        else:
            raise Exceptions.UnsupportableType(start_position)

        if isinstance(end_position, tuple) and len(end_position) == 2:
            end_position = QSize(*end_position)
        elif isinstance(end_position, QSize):
            end_position = end_position
        else:
            raise Exceptions.UnsupportableType(end_position)

        animation = Animation(self._widget_, b'pos', start_position, end_position, duration)
        self._widget_.animations.start(animation)
        return animation

    def geometry(self, end_position: tuple | QPoint, start_position: tuple | QPoint, duration: int = 1000):
        if start_position is None:
            start_position = self._widget_.geometry()

        if isinstance(start_position, tuple) and len(start_position) == 4:
            start_position = QRect(*start_position)
        elif isinstance(start_position, QRect):
            start_position = start_position
        else:
            raise Exceptions.UnsupportableType(start_position)

        if isinstance(end_position, tuple) and len(end_position) == 4:
            end_position = QRect(*end_position)
        elif isinstance(end_position, QRect):
            end_position = end_position
        else:
            raise Exceptions.UnsupportableType(end_position)

        animation = Animation(self._widget_, b'geometry', start_position, end_position, duration)
        self._widget_.animations.start(animation)
        return animation
