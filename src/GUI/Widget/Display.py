from PyAsoka.src.GUI.Widget.ScalableManager import ScalableManager
from PySide6.QtCore import QObject, Property


class Display(ScalableManager):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self._frame_ = Frame(widget, 2, 10, (True, True, True, True))
        self._opacity_ = 1.0
        self.defaultOpacity = 1.0

    @property
    def frame(self):
        return self._frame_

    @property
    def opacity(self):
        return self._opacity_

    @opacity.setter
    def opacity(self, opacity):
        from PyAsoka.src.GUI.Widget.Widget import Widget
        self._opacity_ = opacity

        col = self.widget.style.current
        stl = self.widget.style.default
        colors = [col.background, col.background_line, col.frame, col.line, col.text]
        styles = [stl.background, stl.background_line, stl.frame, stl.line, stl.text]

        for i in range(len(colors)):
            if colors[i] is not None:
                colors[i].setAlpha(int(styles[i].alpha() * opacity))

        for child in self.widget.children():
            if issubclass(type(child), Widget):
                child.display.opacity = opacity

        self.widget.repaint()


class Frame(QObject):
    def __init__(self, widget, thickness: int, angles_radius, rounded_angles: tuple):
        super().__init__()
        self.widget = widget
        self._thickness_ = thickness
        self._angles_radius_ = angles_radius
        self.topLeft = rounded_angles[0]
        self.topRight = rounded_angles[1]
        self.bottomLeft = rounded_angles[2]
        self.bottomRight = rounded_angles[3]

    def setRoundedAngles(self, top_left: bool, top_right: bool, bottom_left: bool, bottom_right: bool):
        self.topLeft = top_left
        self.topRight = top_right
        self.bottomLeft = bottom_left
        self.bottomRight = bottom_right

    @Property(int)
    def anglesRadius(self):
        return self._angles_radius_

    @anglesRadius.setter
    def anglesRadius(self, radius):
        self._angles_radius_ = radius
        self.widget.repaint()

    @Property(int)
    def thickness(self):
        return self._thickness_

    @thickness.setter
    def thickness(self, value):
        self._thickness_ = value
        self.widget.repaint()
