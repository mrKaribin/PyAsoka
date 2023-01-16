from PyAsoka.GUI.Widgets.AWidget import Styles, Style
from PyAsoka.src.GUI.Widgets.ALabelWidget import ALabelWidget

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPalette


class ATextView(ALabelWidget):
    def __init__(self, text: str = '', style: Style = Styles._widget_(), **kwargs):
        super().__init__(QLabel, text=text, style=style, **kwargs)

        self.colors.changed.bind(self.__update_palette__)
        self.__update_palette__()

    def __update_palette__(self):
        palette = self._label_.palette()
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, self.colors.text)
        palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, self.colors.text)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, self.colors.line)
        palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, self.colors.line)
        self._label_.setPalette(palette)

    def setWordWrap(self, state: bool):
        self._label_.setWordWrap(state)

