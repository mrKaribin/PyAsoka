from PyAsoka.src.GUI.Widgets.SimpleTextWidget.SimpleTextWidget import SimpleTextWidget
from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.Asoka import Asoka


class TextEdit(SimpleTextWidget):
    def __init__(self, label='', text='', **kwargs):
        kwargs['style'] = Styles.Input
        super().__init__(label=label, flags=(Asoka.Alignment.AlignLeft, Asoka.TextFlag.TextWordWrap), editable=True, **kwargs)


