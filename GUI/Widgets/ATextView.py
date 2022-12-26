from PyAsoka.GUI.Widgets.AWidget import AWidget, QPaintEvent, QColor, Styles, Style
from PyAsoka.GUI.Widgets.ALabelWidget import ALabelWidget, Qt

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QResizeEvent, QPalette


class ATextView(ALabelWidget):
    def __init__(self, text: str = '', style: Style = Styles.widget(), **kwargs):
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

