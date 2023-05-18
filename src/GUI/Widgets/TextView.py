from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.src.GUI.Widgets.SimpleTextWidget.SimpleTextWidget import SimpleTextWidget
from PyAsoka.Asoka import Asoka


class TextView(SimpleTextWidget):
    def __init__(self, text: str = '', **kwargs):
        if 'style' not in kwargs.keys():
            kwargs['style'] = Styles.Widget

        super().__init__(flags=(Asoka.Alignment.AlignLeft, Asoka.TextFlag.TextSingleLine),
                         visualization=SimpleTextWidget.Visualization.DEFAULT, editable=False, **kwargs)

        self.text.string = text

