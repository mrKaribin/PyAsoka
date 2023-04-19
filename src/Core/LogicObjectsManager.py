from PyAsoka.src.Logic.LogicObject import LogicObject, LogicFunction


class LogicObjectsManager:
    def __init__(self):
        self._objects_ = []

    def add(self, obj: LogicObject):
        self._objects_.append(obj)

    def remove(self, obj: LogicObject):
        self._objects_.remove(obj)

    def list(self):
        return self._objects_
