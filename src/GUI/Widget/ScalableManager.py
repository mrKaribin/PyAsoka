from PySide6.QtCore import Property, QObject


class ScalableManager(QObject):
    def __init__(self):
        super().__init__()
        self.fields = {}

    def set(self, name, val):
        self.fields[name] = val

    def addField(self, _type, name, value=None, setter=None, getter=None):
        self.fields[name] = value
        self.__dict__.update({name, Property(
            _type,
            getter if getter is not None else lambda slf: self.fields[name],
            setter if setter is not None else lambda slf, val: self.set(name, val)
        )})
        # setattr(self.__class__, name, property(
        #     getter if getter is not None else lambda slf: self.fields[name],
        #     setter if setter is not None else lambda slf, val: self.set(name, val)
        # ))
