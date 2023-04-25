from PyAsoka.src.Linguistics.APhraseModel import PhraseModel
from PyAsoka.Core.Logic.AAction import AFunctionAction
from PyAsoka.Connections.AEvent import AEvent
from PyAsoka.Connections.AConnector import AConnector
from PyAsoka.Instruments import Log


class LogicFunction:
    def __init__(self, model: PhraseModel, function, call_type: AConnector.CallbackType = AConnector.CallbackType.DEFAULT):
        self.model = model
        self.function = function
        self.call_type = call_type


class ALogicObject:
    CallType = AConnector.CallbackType
    EventType = AEvent.Type

    def __init__(self, object_model=None):
        if object_model is None:
            object_model = PhraseModel(PhraseModel.Type.NON_LINEAR)
        if isinstance(object_model, str):
            object_model = PhraseModel.parse(object_model)
        self.model = object_model
        self.functions = []
        self.actions = []

    def addFunction(self, model, function, call_type: AConnector.CallbackType = AConnector.CallbackType.DEFAULT):
        if isinstance(model, str):
            model = PhraseModel.parse(model)
        if isinstance(model, PhraseModel):
            self.functions.append(LogicFunction(model, function, call_type))
        else:
            Log.exception_unsupportable_type(type(model))
        return self

    def enable(self):
        from PyAsoka.Processing.AProcess import AProcess
        AProcess.add_task(AProcess.Type.CUSTOM, self.__enable__)

    def __enable__(self):
        for function in self.functions:
            model = PhraseModel(PhraseModel.Type.NON_LINEAR)\
                .add(self.model)\
                .add(function.model)
            self.actions.append(AFunctionAction(model, function.function, call_type=function.call_type))

    def disable(self):
        while len(self.actions) > 0:
            action = self.actions.pop()
            if isinstance(action, AFunctionAction):
                del[action]

    def __del__(self):
        self.disable()
