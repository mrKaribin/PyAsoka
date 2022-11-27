from PySide6.QtWidgets import QGridLayout


class ALayout(QGridLayout):
    def setMargin(self, value: int):
        self.setContentsMargins(value, value, value, value)
