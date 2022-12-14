from PyAsoka.src.GUI.Widget.Widget import Styles, Style
from PyAsoka.src.GUI.Widgets.ALabelWidget import ALabelWidget

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPalette


class TextView(ALabelWidget):
    def __init__(self, text: str = '', style: Style = Styles.widget(), **kwargs):
        super().__init__(QLabel, text=text, style=style, **kwargs)

        self.style.current.changed.bind(self.__update_palette__)
        self.__update_palette__()

    def __update_palette__(self):
        palette = self._label_.palette()
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, self.style.current.text)
        palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, self.style.current.text)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, self.style.current.line)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, self.style.current.line)
        self._label_.setPalette(palette)

    def setWordWrap(self, state: bool):
        self._label_.setWordWrap(state)

