from PyAsoka.src.GUI.Style.Styles import Styles, Style
from PyAsoka.src.GUI.API.API import API
from PyAsoka.src.GUI.Widgets.ALabelWidget import ALabelWidget
from PyAsoka.src.Core.Signal import Signal

from PySide6.QtWidgets import QLineEdit


class LineEdit(ALabelWidget):

    text_changed = Signal(str)
    enter_pressed = Signal(str)

    def __init__(self, text: str = '', style: Style = Styles.Window, **kwargs):
        super().__init__(QLineEdit, text=text, style=style, keyboard=True, **kwargs)
        # self.display.angleRoundingSize = 15

        # class preparation
        # self.colors.changed.bind(self.__update_palette__)
        self.__update_palette__()
        self.setMaximumHeight(self.getTextSize() * 2 + 20)

        self._label_.textChanged.connect(self.__textChanged__)
        API.Keyboard.pressed.bind(self.__keyboard_listener__)

    def setTextSize(self, size: int):
        super().setTextSize(size)
        self.setMaximumHeight(size * 2 + 20)

    def getText(self):
        return self._label_.text()

    def __update_palette__(self):
        self._label_.setStyleSheet(f'background-color: rgba(0, 0, 0, 0);'
                                   f'color: {self.style.current.text.toStyleSheet() if self.style.current.text is not None else "black"};'
                                   f'border-style: outset;')

    def __textChanged__(self, text):
        self.text_changed.emit(self.getText())

    def __keyboard_listener__(self, key):
        if self.isActiveWindow() and key == API.Keyboard.Key.enter:
            self.enter_pressed.emit(self.getText())
