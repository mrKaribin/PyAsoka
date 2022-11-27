from PyAsoka.Connections.AEvent import AEvent
from PyAsoka.Connections.AConnector import AConnector


class Element:
    def __init__(self, name: str):
        self.name = name


class Button(Element):
    def __init__(self, name: str, icon=None):
        super(Button, self).__init__(name)
        self.clicked = AEvent('MenuButtonClicked')
        self.icon = icon

    def connect(self, connector: AConnector):
        self.clicked.connect(connector)
        return self


class Menu(Element):
    def __init__(self, name: str):
        super(Menu, self).__init__(name)
        self.elements = []

    def add(self, element: Element):
        self.elements.append(element)
        return self

    def submenus(self):
        result = []
        for element in self.elements:
            if isinstance(element, Menu):
                result.append(element)
        return result

    def buttons(self):
        result = []
        for element in self.elements:
            if isinstance(element, Button):
                result.append(element)
        return result

    def find_by_name(self, name, _type=None):
        for element in self.elements:
            if element.name == name:
                if _type is None or isinstance(element, _type):
                    return element

        for element in self.elements:
            if isinstance(element, Menu):
                if (result := element.find_by_name(name, _type)) is not None:
                    return result

        return None
