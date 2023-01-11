from pynput.mouse import Controller, Listener

from PyAsoka.src.GUI.API.Screen import Screen
from PyAsoka.src.GUI.API.Keyboard import Keyboard

from PySide6.QtCore import QPoint


class Mouse:
    def __init__(self):
        self.position = QPoint()
        self.click = QPoint()
        self.scroll = QPoint()

        self._mouse_ = Controller()
        self._listener_ = Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self._listener_.start()

    def __call__(self, *args, **kwargs):
        return self._mouse_

    def on_move(self, x, y):
        self.position.x = x
        self.position.y = y

    def on_click(self, x, y, button, pressed):
        self.click.x = x
        self.click.y = y

    def on_scroll(self, x, y, dx, dy):
        self.scroll.x = x
        self.scroll.y = y


class API:
    Mouse = Mouse()
    Keyboard = Keyboard()

    @staticmethod
    def Screen(index):
        return Screen(index)
