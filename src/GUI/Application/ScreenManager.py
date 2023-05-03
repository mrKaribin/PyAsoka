from PyAsoka.src.Core.Object import Object, Signal


class ScreenManager(Object):
    def __init__(self):
        super().__init__()

    @property
    def app(self):
        from PyAsoka.Asoka import Asoka
        return Asoka.app()
