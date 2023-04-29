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

        def getter(key, inst):
            obj = inst._colors_[key]
            return obj.getter(inst)

        def setter(key, inst, value):
            obj = inst._colors_[key]
            obj.setter(inst, value)
            inst.changed.emit()

        for name, color in colors_default.items():
            attrs[name] = QProperty(
                QColor,
                lambda inst, col_name=name: getter(col_name, inst),
                lambda inst, value, col_name=name: setter(col_name, inst, value)
            )

        attrs['_colors_default_'] = colors_default

        return super().__new__(mcs, classname, bases, attrs)


class Style(Object, metaclass=StyleMeta):
    def __init__(self):
        super().__init__()
        self._colors_ = {}
        for name, color in self._colors_default_.items():
            self._colors_[name] = ColorProperty(Color(color.red(), color.green(), color.blue(), color.alpha()))

    @classmethod
    def copy(cls, style):
        return cls()

    def exists(self, color):
        return color in self._colors_.keys()

    @property
    def default(self):
        return type('StyleDefault', (), self._colors_default_)

    changed = Signal()
