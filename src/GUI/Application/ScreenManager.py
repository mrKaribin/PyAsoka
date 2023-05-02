from PyAsoka.src.Graphics.Capture import Capture
from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.Logic.LogicObject import LogicObject, LogicParameter
from PyAsoka.src.Linguistics.PhraseModel import PhraseModel

from PySide6.QtGui import QPixmap, QImage

from threading import Thread
from enum import IntEnum

import time


class SleepScreen(Object):
    logic = LogicObject('[N экран ожидания]')

    frameChanged = Signal(QImage)

    def __init__(self, manager: 'ScreenManager', video_path):
        from PyAsoka.src.GUI.API.API import API
        super().__init__()
        self._manager_ = manager
        self._video_path_ = video_path
        self._resolution_ = (1920, 1080)
        self._thread_: Thread = None
        self._enabled_ = False
        self._stopped_ = True

        for i in range(API.Screens.length):
            size = API.Screens[i].size
            if size.width() / 16 * 9 == size.height() and size.width() > self._resolution_[0]:
                self._resolution_ = (size.width(), size.height())

        self.logic.addFunction('[C включить]', self.enable, LogicObject.ConnectionType.QueuedConnection)
        self.logic.addFunction('[C выключить]', self.disable, LogicObject.ConnectionType.QueuedConnection)

    @property
    def manager(self):
        return self._manager_

    @property
    def enabled(self):
        return self._enabled_

    def enable(self, logic=None):
        from PyAsoka.src.GUI.API.API import API
        if not self._enabled_:
            if self.manager.overlay.enabled:
                self.manager.overlay.disable()

            self._enabled_ = True
            self._stopped_ = False
            self._thread_ = Thread(target=self.__video_run__)
            self._thread_.start()
            for desktop in self.manager.desktops.values():
                desktop.layers.video.enable(500)

            API.Mouse.clicked.connect(self.disable)

    def disable(self, logic=None):
        from PyAsoka.src.GUI.API.API import API
        if self._enabled_:
            self._enabled_ = False
            animation = None

            for desktop in self.manager.desktops.values():
                animation = desktop.layers.video.disappearance(500)
            if animation is not None:
                animation.finished.connect(self.__stop_video__)
            else:
                self.__stop_video__()

            API.Mouse.clicked.disconnect(self.disable)

    def __stop_video__(self):
        self._stopped_ = True
        self._thread_.join()
        self._thread_ = None

    def __video_run__(self):
        from PyAsoka.Asoka import Asoka
        capture = Capture(self._video_path_)
        while True:
            if self._stopped_:
                break

            while (frame := capture.read()) is not False:  # ToDo
                if self._stopped_:
                    break

                frame = frame.toRGB()()
                h, w, ch = frame.shape
                bytesPerLine = ch * w
                image = QImage(frame, w, h, bytesPerLine, QImage.Format.Format_RGB888)
                image = image.scaled(self._resolution_[0], self._resolution_[1],
                                     Asoka.AspectRatio.KeepAspectRatio,
                                     Asoka.TransformationMode.SmoothTransformation)
                self.frameChanged.emit(image)
                del frame
                time.sleep(0.01)

            capture.setPosition(0)
        capture.release()


class Overlay:
    logic = LogicObject('[N рабочий стол]')

    def __init__(self, manager: 'ScreenManager'):
        from PyAsoka.src.GUI.API.API import API
        Symbol, Key = API.Keyboard.Symbol, API.Keyboard.Key

        self._manager_ = manager
        self._enabled_ = False
        self._shortcut_ = API.Keyboard.createShortcut([Key.cmd, Symbol('o')], self.__shortcut_handle__)

        self.logic.addFunction('[C включить]', self.enable, LogicObject.ConnectionType.QueuedConnection)
        self.logic.addFunction('[C выключить]', self.disable, LogicObject.ConnectionType.QueuedConnection)

    @property
    def manager(self):
        return self._manager_

    @property
    def enabled(self):
        return self._enabled_

    def __shortcut_handle__(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def enable(self, logic=None):
        if not self.enabled:
            self._enabled_ = True
            for desktop in self.manager.desktops.values():
                desktop.layers.overlay.enable(300)

    def disable(self, logic=None):
        if self.enabled:
            self._enabled_ = False
            for desktop in self.manager.desktops.values():
                desktop.layers.overlay.disappearance(300)


class ScreenManager:
    def __init__(self):
        from PyAsoka.Asoka import Asoka
        from PyAsoka.src.GUI.Application.Desktop import Desktop
        from PyAsoka.src.GUI.API.API import API

        self._sleep_screen_ = SleepScreen(self, Asoka.Project.Path.Media.Videos() + '\\fireplace.mp4')
        self._overlay_ = Overlay(self)
        self._desktops_ = {}
        for i in range(API.Screens.length):
            screen = API.Screens[i]
            desktop = Desktop(self, screen)
            # desktop.layers.background.disable()
            self.sleepScreen.frameChanged.connect(desktop.__sleep_frame_handle__)
            self._desktops_[i] = desktop
            desktop.show()

    @property
    def sleepScreen(self):
        return self._sleep_screen_

    @property
    def overlay(self):
        return self._overlay_

    @property
    def desktops(self):
        return self._desktops_

    def setPrimalWindow(self, window):
        pass
