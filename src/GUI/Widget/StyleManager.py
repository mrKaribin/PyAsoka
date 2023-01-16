from PyAsoka.src.GUI.Style.Style import Style
from PyAsoka.src.GUI.Style.Styles import Styles


class StyleManager:
    def __init__(self, widget, style: type):
        super(StyleManager, self).__init__()
        self.widget = widget
        style = (Styles.Window if widget.parent() is None else Styles.Widget) if style is None else style
        self._current_ = style()
        self._default_ = style()

        self.current.changed.connect(widget.repaint)

    @property
    def default(self):
        return self._default_

    @property
    def current(self):
        return self._current_

