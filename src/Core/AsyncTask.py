from enum import Enum, auto


class AsyncTask:
    def __init__(self, task):
        self.args: 'list' = None
        self.kwargs: 'dict' = None
        self.task = task
        self.updates = []
        self.results = None

    def start(self, *args, **kwargs):
        from PyAsoka.src.Core.Core import core
        self.args = args,
        self.kwargs = kwargs
        return core().tasks.addTask(self)

    def run(self):
        self.task(self.args, self.kwargs)

    def update(self, *args, **kwargs):
        self.updates.append([args, kwargs])

    def complete(self, *args, **kwargs):
        self.results = [args, kwargs]
