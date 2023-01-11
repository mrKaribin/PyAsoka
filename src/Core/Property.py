from PySide6.QtCore import Property as QProperty


class Property:
    def __init__(self, value=None, _type=None):
        self.value = value
        self.type = _type

    def check(self, value):
        if self.type is not None:
            return isinstance(value, self.type)
        else:
            return True


