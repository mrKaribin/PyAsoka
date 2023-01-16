from PyAsoka.src.GUI.Widget.State import State
from PyAsoka.src.Core.AsynchData import AsynchData
from PyAsoka.src.Core.Object import Object


class StateManager(Object):
    def __init__(self, widget):
        super(StateManager, self).__init__()
        self._widget_ = widget
        self._states_ = {}
        self._active_ = AsynchData([])

    def add(self, name, state: State):
        if name not in self._states_.keys():
            state.name = name
            self.__dict__.update({name: state})
            self._states_[name] = state
            state.enabled.connect(self.__state_enabled__)
            state.disabled.connect(self.__state_disabled__)

    def __state_enabled__(self, layer):
        active = self._active_.lock()
        active.append(layer)
        self._active_.unlock()

    def __state_disabled__(self, layer):
        active = self._active_.lock()
        active.pop(active.index(layer))
        self._active_.unlock()
