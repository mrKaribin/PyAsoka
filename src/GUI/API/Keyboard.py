from pynput import keyboard

from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.Asoka import Asoka


class State:
    def __init__(self):
        self.shift = False
        self.ctrl = False
        self.alt = False

    def __on_press__(self, key):
        if key == keyboard.Key.shift:
            self.shift = True
        if key == keyboard.Key.ctrl:
            self.ctrl = True
        if key == keyboard.Key.alt:
            self.alt = True

    def __on_release__(self, key):
        if key == keyboard.Key.shift:
            self.shift = False
        if key == keyboard.Key.ctrl:
            self.ctrl = False
        if key == keyboard.Key.alt:
            self.alt = False


class Shortcut(Object):
    clicked = Signal()

    def __init__(self, keys: tuple, callback=None, con_type=Asoka.ConnectionType.QueuedConnection):
        super().__init__()
        self._keys_ = {}
        self._enabled_ = True

        for key in keys:
            self._keys_[key] = False

        if callback is not None:
            self.clicked.connect(callback, con_type)

    @property
    def keys(self) -> dict:
        return self._keys_

    @property
    def enabled(self) -> bool:
        return self._enabled_

    def isKeysPressed(self):
        return not False in self._keys_.values()

    def enable(self):
        self._enabled_ = True

    def disable(self):
        self._enabled_ = False


class Keyboard(Object):
    Key = keyboard.Key

    pressed = Signal(Key)
    released = Signal(Key)

    @staticmethod
    def Symbol(code):
        return keyboard.KeyCode.from_char(code)

    def __init__(self):
        super().__init__()
        self.listener = keyboard.Listener(on_press=self.__on_press__, on_release=self.__on_release__)
        self.controller = keyboard.Controller()
        self.state = State()
        self.listener.start()
        self._shortcuts_ = []

    def createShortcut(self, keys, callback=None):
        shortcut = Shortcut(keys, callback)
        self._shortcuts_.append(shortcut)
        return shortcut

    def __on_press__(self, key):
        self.pressed.emit(key)
        self.state.__on_press__(key)
        for shortcut in self._shortcuts_:
            if shortcut.enabled:
                for _key in shortcut.keys.keys():
                    if _key == key:
                        # print(key, True)
                        shortcut.keys[_key] = True
                        if shortcut.isKeysPressed():
                            shortcut.clicked.emit()

    def __on_release__(self, key):
        self.released.emit(key)
        self.state.__on_release__(key)
        for shortcut in self._shortcuts_:
            if shortcut.enabled:
                for _key in shortcut.keys.keys():
                    if _key == key:
                        # print(key, False)
                        shortcut.keys[_key] = False

