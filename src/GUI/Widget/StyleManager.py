from PyAsoka.src.GUI.Style.Style import Style
from PyAsoka.src.GUI.Style.Color import Color


class WidgetStyleMeta(type):
    def __new__(mcs, classname, bases, attrs, style, alpha):
        if style is None:
            raise Exception('Не задан обязательный аргумент style')

        attrs = {}
        colors = style._colors_

        def getter(key, inst):
            col_prop = inst._colors_[key]
            col = col_prop.getter(inst)
            return Color(col.red(), col.green(), col.blue(), col.alpha() * inst._alpha_)

        def setter(key, inst, value):
            col_prop = inst._colors_[key]
            col_prop.setter(inst, value)

        for name, color in colors.items():
            attrs[name] = property(
                lambda inst, key=name: getter(key, inst),
                lambda inst, value, key=name: setter(key, inst, value)
            )

        attrs['_colors_'] = colors
        attrs['_alpha_'] = alpha
        attrs['exists'] = style.exists
        attrs['default'] = style.default

        return super().__new__(mcs, classname, bases, attrs)


class StyleManager:
    def __init__(self, widget, style: type(Style)):
        super(StyleManager, self).__init__()
        self._widget_ = widget
        self._style_ = style()

        self._style_.changed.connect(widget.repaint)

    def __call__(self):
        return self._style_

    @property
    def default(self):
        return self._style_.default

    @property
    def current(self):
        return WidgetStyleMeta('WidgetStyle', (), {}, style=self._style_, alpha=self._widget_.alpha)()

