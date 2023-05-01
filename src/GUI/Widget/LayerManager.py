from PyAsoka.src.GUI.Widget.Layer import Layer
from PyAsoka.src.Core.AsynchData import AsynchData
from PyAsoka.src.Core.Object import Object


class LayerManager(Object):
    def __init__(self, widget):
        super(LayerManager, self).__init__()
        self._widget_ = widget
        self._layers_ = {}
        self._active_ = AsynchData([])

    def __getitem__(self, item):
        return self._layers_[item]

    def add(self, name, layer: Layer):
        if name not in self._layers_.keys():
            layer.name = name
            self.__dict__.update({name: layer})
            self._layers_[name] = layer
            layer.enabled.connect(self.__layer_enabled__)
            layer.disabled.connect(self.__layer_disabled__)
        return self

    def sort(self, active):
        ok = False
        while not ok:
            ok = True
            for i in range(len(active)):
                if i > 0 and active[i - 1].level > active[i].level:
                    active[i-1], active[i] = active[i], active[i-1]
                    ok = False

    def remove(self, name):
        self._layers_.pop(name)
        return self

    def layers(self):
        return self._layers_.values()

    def __layer_enabled__(self, layer):
        active = self._active_.lock()
        active.append(layer)
        self.sort(active)
        self._active_.unlock()

    def __layer_disabled__(self, layer):
        active = self._active_.lock()
        if layer in active:
            active.pop(active.index(layer))
        self._active_.unlock()

    def paint(self, painter, event):
        active = self._active_.lock()
        for layer in active:
            layer.paint(self._widget_, painter, layer.style, self._widget_.props, event)
        self._active_.unlock()
