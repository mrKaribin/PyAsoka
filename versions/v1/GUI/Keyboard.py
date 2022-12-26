from pynput import keyboard

from PyAsoka.Connections.Signal import Signal


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


class Keyboard:
    Key = keyboard.Key

    @staticmethod
    def Simbol(code):
        return keyboard.KeyCode.from_char(code)

    def __init__(self):
        self.listener = keyboard.Listener(on_press=self.__on_press__, on_release=self.__on_release__)
        self.controller = keyboard.Controller()
        self.state = State()
        self.listener.start()
        self.pressed = Signal(keyboard.Key)
        self.released = Signal(keyboard.Key)

    def __on_press__(self, key):
        self.pressed(key)
        self.state.__on_press__(key)

    def __on_release__(self, key):
        self.released(key)
        self.state.__on_release__(key)
