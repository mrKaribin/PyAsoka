from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent


class MouseManager:
    def __init__(self, widget):
        self._widget_ = widget
        self.leftButton = Button()
        self.rightButton = Button()
        self._buttons_ = {
            Qt.MouseButton.LeftButton: self.leftButton,
            Qt.MouseButton.RightButton: self.rightButton
        }
        self.cursorPosition = None
        self.dragging = False

    def button(self, button: Qt.MouseButton):
        return self._buttons_[button]

    def pressEvent(self, event: QMouseEvent):
        widget = self._widget_
        parent = widget.parent()
        if parent is None:
            widget.activateWindow()

        button = self.button(event.button())
        button.pressed = True
        button.pressPosition = event.pos()

    def releaseEvent(self, event: QMouseEvent):
        widget = self._widget_
        if widget.conf.clickable and not widget.mouse.dragging:
            widget.clicked.emit(self)
        widget.mouse.dragging = False

        button = self.button(event.button())
        button.pressed = False
        button.pressPosition = None

    def moveEvent(self, event: QMouseEvent):
        widget = self._widget_
        if widget.conf.movable and widget.mouse.leftButton.pressed:
            lastPos = widget.mouse.leftButton.pressPosition

            if widget.parent() is None:
                pos = event.globalPos()
                widget.move(pos - lastPos)

            else:
                pos = event.globalPos() - widget.parent().pos()
                new_pos = pos - lastPos
                if 0 < new_pos.x() < widget.parent().width() - widget.width() and 0 < new_pos.y() < widget.parent().height() - widget.height():
                    widget.move(pos - lastPos)
            widget.mouse.dragging = True
        self.cursorPosition = event.pos()


class Button:
    def __init__(self):
        self.pressed = False
        self.pressPosition = None
