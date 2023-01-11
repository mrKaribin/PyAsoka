from PyAsoka.src.Core.Signal import Signal, SignalType
from PyAsoka.src.GUI.Animation import Animation
from PyAsoka.src.GUI.AnimationManager import AnimationManager


class Layer:
    def __init__(self, name, func, begin_animation: Animation = None,
                 animation: Animation | AnimationManager = None, end_animation: Animation = None):
        self.name = name
        self.function = func
        self.beginAnimation = begin_animation
        self.animation = animation
        self.endAnimation = end_animation

        self.enabled = Signal(Layer)
        self.disabled = Signal(Layer)

    def enable(self):
        if self.beginAnimation is not None:
            self.beginAnimation.start()
            if self.animation is not None:
                self.beginAnimation.ended.bind(self.animation.start)

        elif self.animation is not None:
            self.animation.start()

        self.enabled(self)

    def disable(self):
        if self.animation is not None:
            self.animation.stop()

        if self.endAnimation is not None:
            self.endAnimation.ended.bind(lambda: self.disabled(self), SignalType.SingleShotConnection)
            self.endAnimation.start()
        else:
            self.disabled(self)

    def paint(self, event):
        self.function(event)
