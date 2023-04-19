from PyAsoka.src.GUI.Animation.Animation import Animation, QPropertyAnimation, Signal
from PySide6.QtCore import QObject


class AnimationManager:
    def __init__(self):
        self._animations_ = []
        self._properties_ = {}
        self._queue_ = []
        self.multiproperty = b'multiproperty'

    def start(self, animation):
        if isinstance(animation, QPropertyAnimation):
            prop = animation.propertyName()
            self._animations_.append(animation)
            animation.start()

    def __addToProperty__(self, prop, animation):
        if prop in self._properties_.keys() and self._properties_[prop] is not None:
            self._properties_[prop] = animation
            return True
        else:
            self._properties_[prop] = [animation]
            return True
