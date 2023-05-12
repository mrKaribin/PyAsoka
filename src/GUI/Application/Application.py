from PyAsoka.src.GUI.Application.ScreenManager import ScreenManager

from PySide6.QtWidgets import QApplication


class Application(QApplication):
    _current_ = None

    def __init__(self, screen_manager: type(ScreenManager), *args, **kwargs):
        super().__init__(*args, **kwargs)
        if screen_manager is None:
            screen_manager = ScreenManager

        Application._current_ = self
        self._manager_ = screen_manager()

    @property
    def manager(self):
        return self._manager_


def app() -> Application:
    return Application._current_
