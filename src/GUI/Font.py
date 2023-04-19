from PySide6.QtGui import QFont


class Font(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
