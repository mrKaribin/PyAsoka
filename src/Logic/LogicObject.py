from PyAsoka.src.Linguistics.PhraseModel import PhraseModel
from PyAsoka.src.Logic.Action import FunctionAction
from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.src.Debug.Exceptions import Exceptions


class LogicParameter:
    def __init__(self, phrase, function):
        self.phrase = phrase,
        self.function = function


class LogicFunction(Object):
    call = Signal(list, dict)

    def __init__(self, model: PhraseModel, callback,
                 _type: FunctionAction.Type = FunctionAction.Type.MOMENTARY,
                 connection_type: Object.ConnectionType = Object.ConnectionType.AutoConnection):
        super().__init__()
        self.model = model
        self.action = FunctionAction(callback, _type)
        self.call.connect(self.action.call, connection_type)


class LogicObject:
    ConnectionType = Object.ConnectionType

    def __init__(self, object_model: PhraseModel | str, auto_enable=True, parent: 'LogicObject' = None):
        if isinstance(object_model, str):
            object_model = PhraseModel.parse(object_model)
        elif isinstance(object_model, PhraseModel):
            pass
        else:
            Exceptions.UnsupportableType(type(object_model))

        self._parent_ = parent
        self._active_ = False
        self._model_ = object_model
        self._functions_ = []
        self._objects_ = []

        if auto_enable:
            from PyAsoka.src.Core.Core import core, Core
            if core() is None:
                Core.Initialization.addObject(self)
                self._active_ = True
            else:
                self.enable()

    @property
    def parent(self):
        return self._parent_

    @property
    def active(self):
        return self._active_

    @property
    def model(self):
        return self._model_

    @property
    def functions(self):
        return self._functions_

    def addFunction(self, model: PhraseModel | str, function,
                    _type: FunctionAction.Type = FunctionAction.Type.MOMENTARY,
                    connection_type: Object.ConnectionType = Object.ConnectionType.AutoConnection):
        if isinstance(model, str):
            model = PhraseModel.parse(model)
        elif isinstance(model, PhraseModel):
            pass
        else:
            Exceptions.UnsupportableType(type(model))

        model = PhraseModel(PhraseModel.Type.NON_LINEAR).add(self.model).add(model)
        self._functions_.append(LogicFunction(model, function, _type, connection_type))
        return self

    def addObject(self, _object: 'LogicObject'):
        _object._parent_ = self
        self._objects_.append(_object)

    def enable(self):
        from PyAsoka.src.Core.Core import core
        self._active_ = True
        core().objects.add(self)

    def disable(self):
        from PyAsoka.src.Core.Core import core
        self._active_ = False
        core().objects.remove(self)

    def __del__(self):
        if self.active:
            self.disable()
