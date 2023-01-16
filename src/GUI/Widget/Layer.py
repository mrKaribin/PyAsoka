from PyAsoka.src.Core.Signal import Signal, SignalType
from PyAsoka.src.Core.Object import Object, ObjectMeta
from PySide6.QtGui import QPainter, QPaintEvent

from enum import IntEnum


class LayerMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs, **extra_kwargs):
        attrs['_level_'] = 1 if 'level' not in extra_kwargs.keys() else extra_kwargs['level']
        attrs['_alpha_'] = 1.0 if 'alpha' not in extra_kwargs.keys() else extra_kwargs['alpha']
        return super().__new__(mcs, name, bases, attrs)


class Layer(Object, metaclass=LayerMeta):
    class Level(IntEnum):
        BOTTOM = 1
        MIDDLE = 2
        TOP = 3

    enabled = Signal(Object)
    disabled = Signal(Object)

    def __init__(self, widget):
        super(Layer, self).__init__()
        self._widget_ = widget
        self.name = ''

    def enable(self):
        self.enabled.emit(self)

    def disable(self):
        self.disabled.emit(self)

    def paint(self, widget, painter: QPainter, event: QPaintEvent):
        pass

    @property
    def level(self):
        return self._level_

    @property
    def alpha(self):
        return self._alpha_

    @property
    def style(self):
        return self._widget_.style
