from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.Connections.Slot import Slot
from PySide6.QtCore import QObject


class WindowManager(QObject):
    windows = []
    win_create = Signal(type, list, tuple)
    gui_connect = Signal(Slot, list, tuple)

    def __init__(self, *args):
        super().__init__(*args)
        WindowManager.gui_connect.bind(WindowManager.__event_happened__)

    @staticmethod
    def openWindow(win_type, args, kwargs):
        from PyAsoka.GUI.Widgets.AWidget import AWidget
        if issubclass(win_type, AWidget):
            # print(f'Пытаюсь открыть окно')
            window = win_type(*args, **kwargs)
            window.emerging()
            WindowManager.windows.append(window)
        else:
            raise Exception("Для открытия окна его класс должен наследоваться от QWidget")

    @staticmethod
    def __open_window__(*args, **kwargs):
        args = list(args)
        win_type = args.pop(0)
        WindowManager.win_create(win_type, args, kwargs)

    @staticmethod
    def __event_happened__(slot, args, kwargs):
        # print(slot, args, kwargs)
        slot(*args, **kwargs)
