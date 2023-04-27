from PyAsoka.src.GUI.API.Screen import Screens, Screen
from PyAsoka.src.GUI.API.Keyboard import Keyboard as KeyboardManager
from PyAsoka.src.GUI.API.Mouse import Mouse as MouseManager


class API:
    Screen = Screen

    Mouse = MouseManager()
    Keyboard = KeyboardManager()
    Screens = Screens()
