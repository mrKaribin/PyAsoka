from PyAsoka.GUI.Widgets.AGifAnimation import AGifAnimation


class ARoundLoader(AGifAnimation):
    def __init__(self, *args, **kwargs):
        super().__init__('loading.gif', *args, **kwargs)
