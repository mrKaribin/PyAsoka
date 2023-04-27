from PySide6.QtWidgets import QApplication


class Application(QApplication):
    _current_ = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Application._current_ = self


def app() -> Application:
    return Application._current_
