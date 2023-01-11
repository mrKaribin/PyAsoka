from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent


class MouseManager:
    def __init__(self):
        self.leftButton = Button()
        self.rightButton = Button()
        self._buttons_ = {
            Qt.MouseButton.LeftButton: self.leftButton,
            Qt.MouseButton.RightButton: self.rightButton
        }
        self.cursorPosition = None

    def button(self, button: Qt.MouseButton):
        return self._buttons_[button]

    def pressEvent(self, event: QMouseEvent):
        button = self.button(event.button())
        button.pressed = True
        button.pressPosition = event.pos()

    def releaseEvent(self, event: QMouseEvent):
        button = self.button(event.button())
        button.pressed = False
        button.pressPosition = None

    def moveEvent(self, event: QMouseEvent):
        self.cursorPosition = event.pos()


class Button:
    def __init__(self):
        self.pressed = False
        self.pressPosition = None
