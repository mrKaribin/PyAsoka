from PyAsoka.src.GUI.Style.Style import Style
from PyAsoka.src.GUI.Style.Styles import Styles


class StyleManager:
    def __init__(self, widget, style):
        super(StyleManager, self).__init__()
        self.widget = widget
        self._current_ = (Styles.window() if widget.parent() is None else Styles.widget()) if style is None else style
        self._default_ = Style.copy(self.current)

        self.current.changed.connect(widget.repaint)

    @property
    def default(self):
        return self._default_

    @property
    def current(self):
        return self._current_

