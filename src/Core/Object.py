from PySide6.QtCore import QObject, Qt, Slot
from PyAsoka.src.Core.Property import Property, PropertyImpl
from PyAsoka.src.Core.Signal import Signal


class ObjectMeta(type(QObject)):
    def __new__(cls, name, bases, attrs):
        attrs['_properties_'] = {}
        for key in list(attrs.keys()):
            attr = attrs[key]
            if isinstance(attr, Property):
                type_ = attr.type
                notifier = Signal(type_)
                attrs[key] = PropertyImpl(type_=type_, name=key, notify=notifier)
                attrs[f'_{key}_'] = attr.value
                attrs[f'{key}Changed'] = notifier
                attrs['_properties_'][key] = attrs[key]
        return super().__new__(cls, name, bases, attrs)


class Object(QObject, metaclass=ObjectMeta):
    ConnectionType = Qt.ConnectionType

    def __init__(self):
        super(Object, self).__init__()
