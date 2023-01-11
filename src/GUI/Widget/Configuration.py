

class Configuration:
    def __init__(self, widget, opacity):
        self.widget = widget
        self.display = Display(widget, opacity)


class Display:
    def __init__(self, widget, opacity):
        self.widget = widget
        self._opacity_ = opacity

    def __get_opacity__(self):
        return self._opacity_

    def __set_opacity__(self, opacity):
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
                child.conf.display.__set_opacity__(opacity)

        self.widget.repaint()
