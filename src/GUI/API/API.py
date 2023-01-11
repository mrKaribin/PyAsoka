from PyAsoka.src.GUI.API.Screen import Screen
from PyAsoka.src.GUI.API.Keyboard import Keyboard as KeyboardManager
from PyAsoka.src.GUI.API.Mouse import Mouse as MouseManager


class API:
    Mouse = MouseManager()
    Keyboard = KeyboardManager()

    @staticmethod
    def Screen(index):
        return Screen(index)
