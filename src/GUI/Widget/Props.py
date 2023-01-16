from PyAsoka.src.Core.Object import Object, ObjectMeta
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.GUI.Widget.Prop import Prop
from PySide6.QtCore import QObject, Property


class PropsMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs, **extra_kwargs):
        props_list = {}
        for base in bases:
            if f'_props_list_' in base.__dict__.keys():
                props_list = {**props_list, **dict(base.__dict__[f'_props_list_'])}

        props_fields = {}
        props_static_fields = {}
        props_classes = {}
        for key in list(attrs.keys()):
            attr = attrs[key]
            attr_name = key[0].lower() + key[1:]
            if isinstance(attr, Prop) or (isinstance(attr, type) and (issubclass(attr, Prop) or type(attr) == type)):
                if type(attr) == type:
                    print(attr)
                props_list[attr_name] = attr
                attrs.pop(key)

        for key, attr in props_list.items():
            if isinstance(attr, Prop):
                props_fields[key] = attr

            elif isinstance(attr, type):
                if issubclass(attr, Prop):
                    props_static_fields[key] = attr

                elif type(attr) == type:
                    props_classes[key] = attr

        attrs[f'_props_list_'] = props_list

        def setter(prop_name, inst, value):
            obj = getattr(inst, f'_{prop_name}_')
            obj.__setter__(inst, value)
            obj.changed.emit()

        def getter(prop_name, inst):
            obj = getattr(inst, f'_{prop_name}_')
            return obj.__getter__(inst)

        for key, prop in props_fields.items():
            attrs[key] = Property(
                prop.type,
                lambda inst: getter(key, inst),
                lambda inst, value: setter(key, inst, value)
            )

        for key, prop in props_static_fields.items():
            attrs[key] = Property(
                prop._type_,
                lambda inst: getter(key, inst),
                lambda inst, value: setter(key, inst, value)
            )

        for key, prop in props_classes.items():
            props_attrs = dict(prop.__dict__)

            for props_key in list(props_attrs.keys()):
                attr = props_attrs[props_key]
                if not (isinstance(attr, Prop) or isinstance(attr, type)):
                    props_attrs.pop(props_key)

            props_classes[key] = PropsMeta('Properties', (Props, ), props_attrs)

        attrs['_props_fields_'] = props_fields
        attrs['_props_static_fields_'] = props_static_fields
        attrs['_props_classes_'] = props_classes

        return super().__new__(mcs, name, bases, attrs)


class Props(Object, metaclass=PropsMeta):
    def __init__(self, widget):
        super().__init__()
        self._widget_ = None

        for key, prop in self._props_fields_.items():
            self.__dict__.update({f'_{key}_': type(prop)(prop.type, prop.value, self._widget_)})

        for key, prop in self._props_static_fields_.items():
            self.__dict__.update({f'_{key}_': prop(widget=self._widget_)})

        for key, prop in self._props_classes_.items():
            self.__dict__.update({f'{key}': prop(self._widget_)})
