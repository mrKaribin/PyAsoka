from PyAsoka.src.GUI.Widget.Layer import Layer


class LayerManager:
    def __init__(self):
        self._layers_ = {}
        self._active_ = {}

    def __getitem__(self, item):
        return self._layers_[item]

    def add(self, layer: Layer):
        if layer.name not in self._layers_.keys():
            self.__dict__.update({layer.name: layer})
            self._layers_[layer.name] = layer
            layer.enabled.bind(self.__layer_enabled__)
            layer.disabled.bind(self.__layer_disabled__)
        return self

    def remove(self, name):
        self._layers_.pop(name)
        return self

    def layers(self):
        return self._layers_.values()

    def active(self):
        return self._active_.values()

    def __layer_enabled__(self, layer):
        self._active_[layer.name] = layer

    def __layer_disabled__(self, layer):
        self._active_.pop(layer.name)

    def enable(self, name: str):
        if name in self._layers_.keys():
            self._layers_[name].enable()

    def disable(self, name):
        if name in self._active_.keys():
            self._active_[name].disable()

    def paint(self, widget):
        for layer in self._active_.values():
            layer.paint(widget)
