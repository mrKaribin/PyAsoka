from PySide6.QtCore import QSize, QPoint
from PySide6.QtWidgets import QApplication


class Screen:
    def __init__(self, screen):
        self.index = 0

        if isinstance(screen, int):
            self.index = screen
        if isinstance(screen, QPoint):
            screen = QApplication.screenAt(screen)
            self.index = QApplication.screens().index(screen)

    def information(self):
        print(f'Size: {QApplication.screens()[self.index].size()}')
        print(f'Aval size: {QApplication.screens()[self.index].availableSize()}')
        print(f'Virt size: {QApplication.screens()[self.index].virtualSize()}')
        print(f'Phys size: {QApplication.screens()[self.index].physicalSize()}')
        print(f'Aval virt size: {QApplication.screens()[self.index].availableVirtualSize()}')
        print(f'Aval geometry: {QApplication.screens()[self.index].availableGeometry()}')
        print(f'Aval virt geometry: {QApplication.screens()[self.index].availableVirtualGeometry()}')

    def getSize(self):
        return QApplication.screens()[self.index].size()

    def getAvailableSize(self):
        return QApplication.screens()[self.index].availableSize()

    def getAvailableGeometry(self):
        return QApplication.screens()[self.index].availableGeometry()
