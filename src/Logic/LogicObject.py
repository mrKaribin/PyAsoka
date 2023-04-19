from PyAsoka.src.Linguistics.APhraseModel import APhraseModel
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

    def __init__(self, model: APhraseModel, callback,
                 _type: FunctionAction.Type = FunctionAction.Type.MOMENTARY,
                 connection_type: Object.ConnectionType = Object.ConnectionType.AutoConnection):
        super().__init__()
        self.model = model
        self.action = FunctionAction(callback, _type)
        self.call.connect(self.action.call, connection_type)


class LogicObject:
    ConnectionType = Object.ConnectionType

    def __init__(self, object_model: APhraseModel | str, auto_enable=True):
        if isinstance(object_model, str):
            object_model = APhraseModel.parse(object_model)
        elif isinstance(object_model, APhraseModel):
            pass
        else:
            Exceptions.UnsupportableType(type(object_model))

        self._active_ = False
        self._model_ = object_model
        self._functions_ = []

        if auto_enable:
            from PyAsoka.src.Core.Core import core, Core
            if core() is None:
                Core.Initialization.addObject(self)
                self._active_ = True
            else:
                self.enable()


    @property
    def active(self):
        return self._active_

    @property
    def model(self):
        return self._model_

    @property
    def functions(self):
        return self._functions_

    def addFunction(self, model: APhraseModel | str, function,
                    _type: FunctionAction.Type = FunctionAction.Type.MOMENTARY,
                    connection_type: Object.ConnectionType = Object.ConnectionType.AutoConnection):
        if isinstance(model, str):
            model = APhraseModel.parse(model)
        elif isinstance(model, APhraseModel):
            pass
        else:
            Exceptions.UnsupportableType(type(model))

        model = APhraseModel(APhraseModel.Type.NON_LINEAR).add(self.model).add(model)
        self._functions_.append(LogicFunction(model, function, _type, connection_type))
        return self

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
