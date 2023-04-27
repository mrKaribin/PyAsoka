from PyAsoka.src.GUI.Widget.Widget import Widget
from PyAsoka.src.GUI.Style.Styles import Styles
from PyAsoka.src.GUI.API.API import API


class Desktop(Widget):

    class Colors:


    def __init__(self, screen: API.Screen):
        super().__init__(style=Styles.Desktop, geometry=screen.geometry)
        self._
