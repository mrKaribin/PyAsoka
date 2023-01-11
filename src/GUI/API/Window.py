import os
from PyAsoka.src.GUI.winlaunch.winlaunch import *


class Window:
    win_id = None

    @staticmethod
    def update():
        Window.win_id = os.popen('xdotool getactivewindow').read()

    @staticmethod
    def get_pos():
        if Window.win_id is not None and (buf := win_pos(Window.win_id)) is not None:
            return list(buf)
        else:
            return None

    @staticmethod
    def get_size():
        if Window.win_id is not None and (buf := win_size(Window.win_id)) is not None:
            return list(buf)
        else:
            return None
