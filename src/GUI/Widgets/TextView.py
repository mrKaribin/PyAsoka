from PyAsoka.src.GUI.Style.Styles import Styles, Style
from PyAsoka.src.GUI.Widgets.ALabelWidget import ALabelWidget
from PyAsoka.src.GUI.Widgets.TextWidget import TextWidget, QFontMetrics
from PyAsoka.Asoka import Asoka

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPalette


class TextView(TextWidget):
    def __init__(self, text: str = '', **kwargs):
        if 'style' not in kwargs.keys():
            kwargs['style'] = Styles.Widget

        super().__init__(flags=Asoka.Alignment.AlignLeft | Asoka.TextFlag.TextSingleLine,
                         visualization=TextWidget.Visualization.DEFAULT, single_line=True, editable=False, **kwargs)

        self.text.string = text

