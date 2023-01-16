

class Configuration:
    def __init__(self, widget, movable, clickable):
        self.widget = widget
        self._movable_ = movable
        self._clickable_ = clickable

    @property
    def movable(self):
        return self._movable_

    @movable.setter
    def movable(self, value):
        if isinstance(value, bool):
            self._movable_ = value

    @property
    def clickable(self):
        return self._clickable_

    @clickable.setter
    def clickable(self, value):
        if isinstance(value, bool):
            self._clickable_ = value
