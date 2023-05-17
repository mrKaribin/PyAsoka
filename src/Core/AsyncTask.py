from enum import Enum, auto


class AsyncTask:
    def __init__(self, *args, **kwargs):
        self._id_: int = id(self)
        self.args: 'tuple' = args
        self.kwargs: 'dict' = kwargs
        self.update_callback = None
        self.complete_callback = None
        self.results = None

    @property
    def id(self):
        return self._id_

    def setUpdateCallback(self, callback):
        self.update_callback = callback

    def setCompleteCallback(self, callback):
        self.complete_callback = callback

    def start(self, parent=None, *args, **kwargs):
        from PyAsoka.src.Core.Core import core
        if args:
            self.args = args,
        if kwargs != {}:
            self.kwargs = kwargs
        return core().tasks.addTask(self, parent=parent)

    def run(self):
        self.task(*self.args, **self.kwargs)

    def update(self, *args, **kwargs):
        if self.update_callback is not None:
            self.update_callback(self.id, args, kwargs)

    def complete(self, *args, **kwargs):
        if self.complete_callback is not None:
            self.complete_callback(self.id, args, kwargs)

    def haveUpdateHandler(self):
        return not self.__class__.onUpdate == AsyncTask.onUpdate

    def haveCompleteHandler(self):
        return not self.__class__.onComplete == AsyncTask.onComplete

    def task(self, *args, **kwargs):
        pass

    def onUpdate(self, *args, **kwargs):
        pass

    def onComplete(self, *args, **kwargs):
        pass
