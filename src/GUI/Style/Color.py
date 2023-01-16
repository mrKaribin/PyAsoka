from PySide6.QtGui import QColor


class Color(QColor):
    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255, color: QColor = None):
        super().__init__()

        if isinstance(color, QColor) or isinstance(color, Color):
            self.setRgb(
                color.red(),
                color.green(),
                color.blue(),
                color.alpha()
            )
        else:
            self.setRgb(r, g, b, a)

    def toStyleSheet(self):
        return f'rgba({self.red()}, {self.green()}, {self.blue()}, {self.alpha()})'
