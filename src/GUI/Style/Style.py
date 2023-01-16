from PyAsoka.src.Core.Object import Object
from PyAsoka.src.Core.Property import Property
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.GUI.Style.Color import Color, QColor
from PyAsoka.src.Debug.Exceptions import Exceptions


class Style(Object):

    frame = Property(Color)
    background = Property(Color)
    background_line = Property(Color)
    line = Property(Color)
    text = Property(Color)

    changed = Signal()

    @staticmethod
    def copy(style):
        return Style(**style._colors_)

    def __init__(self, **kwargs):
        super(Style, self).__init__()
        self._colors_ = {}

        for name, color in kwargs.items():
            if isinstance(color, Color) and name in self._properties_.keys():
                prop = self._properties_[name]
                if issubclass(prop.type, Color):
                    setattr(self, f'_{name}_', color)
                    self._colors_[name] = Color(color.red(), color.green(), color.blue(), color.alpha())
