from PyAsoka.src.Core.Object import Object, ObjectMeta
from PyAsoka.src.Core.Property import Property, QProperty
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.GUI.Style.Color import Color, ColorProperty, QColor
from PyAsoka.src.Debug.Exceptions import Exceptions


class StyleMeta(ObjectMeta):
    def __new__(mcs, classname, bases, attrs, **extra_kwargs):
        colors_default = {}
        for base in bases:
            if f'_colors_default_' in base.__dict__.keys():
                colors_default = {**colors_default, **base.__dict__[f'_colors_default_']}

        for name, arg in extra_kwargs.items():
            if isinstance(arg, Color):
                colors_default[name] = arg

        colors = {}
        for name, color in colors_default.items():
            prop = ColorProperty(color)
            attrs[name] = QProperty(
                QColor,
                prop.getter,
                prop.setter
            )
            colors[f'_{name}_'] = prop

        return super().__new__(mcs, classname, bases, attrs)


class Style(Object, metaclass=StyleMeta):
    def __init__(self):
        super().__init__()

    @classmethod
    def copy(cls, style):
        return cls()

    changed = Signal()
