from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import QScreen
from PyAsoka.src.GUI.Application.Application import Application
from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.src.Debug.Exceptions import Exceptions
from PyAsoka.Asoka import Asoka

import os


class Screen:
    def __init__(self, screen: QScreen):
        self._screen_ = screen

    def __str__(self):
        print(f'Size: {self.size}')
        print(f'Aval size: {self.availableSize}')
        print(f'Aval geometry: {self.geometry}')
        print(f'Aval virt geometry: {self.availableGeometry}')

    @property
    def size(self):
        return self._screen_.size()

    @property
    def geometry(self):
        return self._screen_.geometry()

    @property
    def availableSize(self):
        return self._screen_.availableSize()

    @property
    def availableGeometry(self):
        return self._screen_.availableGeometry()

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


class Screens:
    def __getitem__(self, item: int):
        if isinstance(item, int):
            if 0 <= item < len(Application.screens()):
                return Screen(Application.screens()[item])
            else:
                raise Exceptions.ValueIsOutOfRange(item, -1, len(Application.screens()))
        else:
            raise Exceptions.UnsupportableType(item)

    @property
    def main(self):
        return self[0]

    @property
    def length(self):
        return len(Application.screens())

