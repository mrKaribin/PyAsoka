from PySide6.QtCore import QSize, QPoint
from PySide6.QtWidgets import QApplication
from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.Asoka import Asoka

import os


class Screen:
    def __init__(self, screen=0):
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

    def enable(self):
        if Asoka.Device.getOS() == Asoka.Device.OS.WINDOWS:
            from win32con import HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MOUSEEVENTF_MOVE
            from win32gui import SendMessage
            from win32api import mouse_event
            SendMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, -1)
            mouse_event(MOUSEEVENTF_MOVE, 0, 0)
            Logs.message('Display enabled')
        elif Asoka.Device.getOS() == Asoka.Device.OS.LINUX:
            os.system('xset -display :0.0 dpms force on')

    def disable(self):
        if Asoka.Device.getOS() == Asoka.Device.OS.WINDOWS:
            from win32con import HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER
            from win32gui import SendMessage
            SendMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
            Logs.message('Display disabled')
        elif Asoka.Device.getOS() == Asoka.Device.OS.LINUX:
            os.system('sleep 1 && xset -display :0.0 dpms force off ')

