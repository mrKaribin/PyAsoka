from PyAsoka.src.GUI.Widget.Widget import Widget, QPainter, Props, QPaintEvent, QRect
from PyAsoka.src.GUI.Widgets.IconView import IconView
from PyAsoka.src.GUI.Widgets.TextWidget import TextWidget, QFontMetrics
from PyAsoka.src.GUI.Widget.State import State
from PyAsoka.src.GUI.Widget.Layer import Layer
from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.Asoka import Asoka

from enum import IntEnum


class LineEdit(TextWidget):
    class Type(IntEnum):
        DEFAULT = 1
        PASSWORD = 2

    def __init__(self, type: Type = Type.DEFAULT, height: int = 40, label: str = '', **kwargs):
        kwargs['style'] = Styles.Input
        if type == LineEdit.Type.PASSWORD:
            visualization = LineEdit.Visualization.SECRET
        else:
            visualization = LineEdit.Visualization.DEFAULT

        super().__init__(flags=Asoka.Alignment.AlignLeft | Asoka.TextFlag.TextSingleLine,
                         visualization=visualization,
                         label=label,
                         single_line=True,
                         editable=True, **kwargs)
        self._type_ = type
        self.setFixedHeight(height)
        self.text.font.setPixelSize(int(self.height() * 0.40))
        self.text.indent.top = (self.height() - QFontMetrics(self.text.font).height()) // 2
        # self.text.font.setPointSize(self.height() // 3)

        if type == self.Type.PASSWORD:
            self.text.visualization = self.Visualization.SECRET
            self.modifier = IconView(Asoka.Project.Path.Asoka.Media.Icons() + '\\lock.png', parent=self, clickable=True)
            self.resized.connect(self.modifierFix)
            self.modifier.clicked.connect(self.modifierClicked)

    @property
    def type(self):
        return self._type_

    def modifierFix(self):
        size = self.height() / 3 * 2
        indent = (self.height() - size) // 2
        self.modifier.geometry = (self.width() - size - indent, indent, size, size)

    def modifierClicked(self):
        if self.type == self.Type.PASSWORD:
            if self.text.visualization == self.Visualization.DEFAULT:
                self.text.visualization = self.Visualization.SECRET
            else:
                self.text.visualization = self.Visualization.DEFAULT
        self.repaint()
