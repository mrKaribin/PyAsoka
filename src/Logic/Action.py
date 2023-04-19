from enum import Enum, auto


class ActionPrototype:
    class Type(Enum):
        MOMENTARY = auto()
        CONTINUOUS = auto()


class FunctionAction(ActionPrototype):
    def __init__(self, callback, _type: ActionPrototype.Type = ActionPrototype.Type.MOMENTARY):
        super().__init__()
        self.callback = callback
        self.type = _type

    def call(self, args, kwargs):
        self.callback(*args, **kwargs)
