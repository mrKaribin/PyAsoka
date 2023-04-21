from PyAsoka.src.GUI.Widget.AnimationManager import Animation
from PyAsoka.src.GUI.Style.Color import Color, QColor
from PyAsoka.src.Debug.Exceptions import Exceptions
from PySide6.QtCore import QPoint, QRect, QSize


class Animate:
    def __init__(self, widget):
        self._widget_ = widget

    @property
    def widget(self):
        return self._widget_

    def size(self, end_size: tuple | QSize, start_size: tuple | QSize = None, duration: int = 1000, silent=False):
        if start_size is None:
            start_size = self._widget_.size

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

        start_geom = QRect(self._widget_.position, start_size)
        end_geom = QRect(self._widget_.position, end_size)
        animation = Animation(self._widget_, b'geometry', start_geom, end_geom, duration)
        if silent:
            self.widget._formal_geometry_ = end_geom
        else:
            self.widget.formalSize = end_geom.size()
        self._widget_.animations.start(animation)
        return animation

    def position(self, end_position: tuple | QPoint, start_position: tuple | QPoint = None, duration: int = 1000, silent=False):
        if start_position is None:
            start_position = self._widget_.position

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
        if silent:
            self.widget._formal_geometry_ = QRect(end_position, self.widget.formalGeometry.size())
        else:
            self.widget.formalPosition = end_position
        self._widget_.animations.start(animation)
        return animation

    def geometry(self, end_position: tuple | QRect, start_position: tuple | QRect = None, duration: int = 1000, silent=False):
        if start_position is None:
            start_position = self._widget_.geometry

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
        if silent:
            self.widget._formal_geometry_ = end_position
        else:
            self.widget.formalGeometry = end_position
        self._widget_.animations.start(animation)
        return animation

    def color(self, color_name: str, end_color: tuple | Color | QColor, start_color: tuple | Color | QColor = None, duration = 1000):
        if start_color is None:
            start_color = self.widget.style.getColor(color_name)

        if isinstance(start_color, tuple) and 3 <= len(start_color) <= 4:
            start_color = QColor(*end_color)
        elif isinstance(start_color, QColor):
            pass
        else:
            raise Exceptions.UnsupportableType(start_color)

        if isinstance(end_color, tuple) and 3 <= len(end_color) <= 4:
            end_color = QColor(*end_color)
        elif isinstance(end_color, QColor):
            pass
        else:
            raise Exceptions.UnsupportableType(end_color)

        animation = Animation(self.widget.style(), bytes(color_name, 'utf-8'), start_color, end_color, duration)
        self.widget.animations.start(animation)
        return animation

    def opacity(self, end_value: float, start_value: float = None, duration: int = 1000):
        if start_value is None:
            start_value = self.widget.alpha

        if isinstance(start_value, int):
            start_value = float(start_value)
        elif isinstance(start_value, float):
            pass
        else:
            raise Exceptions.UnsupportableType(start_value)

        if isinstance(end_value, int):
            end_value = float(start_value)
        elif isinstance(end_value, float):
            pass
        else:
            raise Exceptions.UnsupportableType(start_value)

        animation = Animation(self.widget.props, b'alpha', start_value, end_value, duration)
        self.widget.animations.start(animation)
        return animation
