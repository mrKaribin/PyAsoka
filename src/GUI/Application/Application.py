from PySide6.QtWidgets import QApplication
from PyAsoka.src.GUI.Application.ScreenManager import ScreenManager


class Application(QApplication):
    _current_ = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Application._current_ = self
        self._manager_ = ScreenManager()

    @property
    def manager(self):
        return self._manager_


def app() -> Application:
    return Application._current_
