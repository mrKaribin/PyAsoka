from PySide6.QtCore import Property as QProperty


class Property:
    def __init__(self, _type, initial_state=None, notify=False):
        self.type = _type
        self.value = initial_state
        self.notify = notify


class PropertyImpl(QProperty):
    def __init__(self, type_, name, notify):
        super().__init__(type_, self.getter, self.setter, notify=notify)
        self.type = type_
        self.name = name
        self.notify = notify

    def getter(self, instance):
        return getattr(instance, f'_{self.name}_')

    def setter(self, instance, value):
        setattr(instance, f'_{self.name}_', value)
        if self.notify:
            signal = getattr(instance, f'{self.name}Changed')
            signal.emit(value)
