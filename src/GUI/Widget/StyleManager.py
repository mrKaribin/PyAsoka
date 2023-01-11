from PyAsoka.src.GUI.Style.Style import Style
from PyAsoka.src.GUI.Style.Styles import Styles


class StyleManager:
    def __init__(self, widget, style):
        self.widget = widget
        self._default_ = (Styles.window() if widget.parent() is None else Styles.widget()) if style is None else style
        self._current_ = Style(self.default)

        self.current.changed.bind(widget.repaint)

    @property
    def default(self):
        return self._default_

    @property
    def current(self):
        return self._current_

