

class Id:
    DEFAULT_NAME = 'default'

    def __init__(self, name: str = None):
        from PyAsoka.Processing.AProcess import AProcess
        self.id, self.__unique_name__ = AProcess.current_process.create_id(name)
        if self.__unique_name__ is None:
            self.__unique_name__ = Id.DEFAULT_NAME

    def __call__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, Id):
            return self.id == other.id
        return False

    def name(self):
        return self.__unique_name__

    def bind(self, parent):
        self.__object__ = parent
        return self

    def get_object(self):
        return self.__object__
