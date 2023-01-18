from PyAsoka.src.Core.Object import Object, ObjectMeta
from PyAsoka.src.Core.Signal import Signal


class PropMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs, **extra_kwargs):
        if name != 'Prop':
            if 'type' not in extra_kwargs:
                raise Exception('Не указан тип свойства')
            if 'default' not in extra_kwargs:
                raise Exception('Не указано значение свойства по умолчанию')

            attrs['_type_'] = extra_kwargs['type']
            attrs['_value_'] = extra_kwargs['default']
            attrs['changed'] = Signal(extra_kwargs['type'])
        return super().__new__(mcs, name, bases, attrs)


class Prop(Object, metaclass=PropMeta):
    def __init__(self, _type=None, initial_state=None, widget=None):
        super().__init__()

        name = self.__class__.__name__
        if name == 'Prop':
            if _type is None:
                raise Exception('Не указан тип свойства')
            if initial_state is None:
                raise Exception('Не указано значение свойства по умолчанию')

            self.type = _type
            self.value = initial_state
        else:
            self.type = self._type_
            self.value = self._value_

        self._widget_ = widget

    def __setter__(self, inst, value):
        self.setter(self._widget_, value)
        self.changed.emit(value)

    def __getter__(self, inst):
        return self.getter(self._widget_)

    def setter(self, widget, value):
        self.value = value

    def getter(self, widget):
        return self.value
