from PyAsoka.src.Core.Signal import Signal, SignalType
from PyAsoka.src.Core.Object import Object, ObjectMeta
from PyAsoka.src.GUI.Widget.Props import Props
from PyAsoka.src.GUI.Widget.StyleManager import WidgetStyleMeta
from PyAsoka.src.GUI.Animation.Animation import Animation
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Property

from enum import IntEnum


class LayerMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs, **extra_kwargs):

        attrs['_level_'] = 1 if 'level' not in extra_kwargs.keys() else extra_kwargs['level']

        def getter(inst):
            return inst._alpha_

        def setter(inst, value):
            inst._alpha_ = value
            inst.alphaChanged.emit(value)

        attrs['_alpha_'] = 1.0 if 'alpha' not in extra_kwargs.keys() else extra_kwargs['alpha']
        attrs['alpha'] = Property(float, getter, setter)
        attrs['alphaChanged'] = Signal(float)

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
        self.alphaChanged.connect(widget.repaint)
        self.animation = None

    def enable(self):
        self.enabled.emit(self)

    def disable(self):
        self.disabled.emit(self)

    def disappearance(self):
        animation = Animation(self, b'alpha', self.alpha, 0.0, 500)
        animation.finished.connect(self.disable)
        self.animation = animation
        animation.start()
        return animation

    def paint(self, widget, painter: QPainter, style, props: Props, event: QPaintEvent):
        pass

    @property
    def level(self):
        return self._level_

    @property
    def style(self):
        return WidgetStyleMeta('LayerStyle', (), {}, style=self._widget_.style(), alpha=self._widget_.alpha * self.alpha)()
