from PyAsoka.src.Core.Object import Object, ObjectMeta
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.GUI.Widget.Prop import Prop
from PySide6.QtCore import QObject, Property


class PropsMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs, **extra_kwargs):
        props_list = {}
        for base in bases:
            if f'_props_' in base.__dict__.keys():
                props_list = {**props_list, **base.__dict__[f'_props_list_']}

        if f'_props_list_' not in attrs:
            attrs[f'_props_list_'] = {}
        props_list = {**attrs[f'_props_list_'], **props_list}

        for key in list(attrs.keys()):
            attr = attrs[key]
            cond1 = isinstance(attr, Prop)
            cond2 = isinstance(attr, type) and (issubclass(attr, Prop) or issubclass(attr, Props))
            if cond1 or cond2:
                attrs.pop(key)
                lay_name = key[0].lower() + key[1:]
                props_list[lay_name] = attr

        attrs[f'_props_list_'] = props_list
        props = {}
        for key, member in props_list.items():
            if isinstance(member, type):
                prop = member()
            else:
                prop = member

            if isinstance(prop, Props):
                attrs[key] = prop
                props[key] = prop

            if isinstance(prop, Prop):
                def setter(inst, value):
                    prop.__setter__(inst, value)
                    getattr(inst, f'_{key}_changed_').emit()

                attrs[key] = Property(
                    prop.type,
                    prop.__getter__,
                    prop.__setter__
                )
                props[key] = prop
        attrs[f'_props_'] = props

        return super().__new__(mcs, name, bases, attrs)


class Props(Object, metaclass=PropsMeta):
    def __init__(self):
        super().__init__()
        self._widget_ = None

    def setWidget(self, widget):
        self._widget_ = widget
        for name, prop in self._props_.items():
            prop.setWidget(widget)
            if isinstance(prop, Prop):
                prop.changed.connect(widget.repaint)
