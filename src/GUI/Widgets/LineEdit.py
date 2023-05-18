from PyAsoka.src.GUI.Widgets.IconView import IconView
from PyAsoka.src.GUI.Widgets.SimpleTextWidget.SimpleTextWidget import SimpleTextWidget, QFontMetrics
from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.Asoka import Asoka

from enum import IntEnum


class LineEdit(SimpleTextWidget):
    class Type(IntEnum):
        DEFAULT = 1
        PASSWORD = 2

    def __init__(self, type: Type = Type.DEFAULT, label: str = '', **kwargs):
        kwargs['style'] = Styles.Input
        if 'stretch' not in kwargs.keys():
            kwargs['stretch'] = (True, False)
        if 'min_size' not in kwargs.keys():
            kwargs['min_size'] = (100, 35)

        if type == LineEdit.Type.PASSWORD:
            visualization = LineEdit.Visualization.SECRET
        else:
            visualization = LineEdit.Visualization.DEFAULT

        super().__init__(flags=(Asoka.Alignment.AlignLeft, Asoka.TextFlag.TextSingleLine),
                         visualization=visualization, label=label, editable=True, **kwargs)
        self._type_ = type
        # self.text.font.setPointSize(self.height() // 3)

        if type == self.Type.PASSWORD:
            self.text.visualization = self.Visualization.SECRET
            self.modifier = IconView(Asoka.Project.Path.Asoka.Media.Icons() + '\\lock.png', parent=self, clickable=True)
            self.resized.connect(self.modifierFix)
            self.modifier.clicked.connect(self.modifierClicked)

        self.resized.connect(self.updateTextProperties)

    @property
    def type(self):
        return self._type_

    def updateTextProperties(self):
        self.text.font.setPixelSize(int(self.height() * 0.40))
        self.text.indent.top = (self.height() - QFontMetrics(self.text.font).height()) // 2

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
