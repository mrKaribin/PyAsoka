from PyAsoka.GUI.Widgets.AWidget import AWidget


class Window(AWidget):

    class States:
        JUMPING = 'JUMPING'

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        print(self.States.__dict__)
