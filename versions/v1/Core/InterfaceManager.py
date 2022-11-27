from PyAsoka.Instruments import Log

from PyAsoka.Processing.AProcess import Headers


class Interface:
    def __init__(self, header: Headers, cutaway, callback=None):
        self.header = header
        self.cutaway = cutaway
        self.callback = callback


class InterfaceManager:
    def __init__(self):
        self.interfaces = []

    def __call__(self, *args, **kwargs):
        return self.interfaces

    def add(self, header, cutaway, callback=None):
        self.interfaces.append(Interface(header, cutaway))

    def remove(self, header):
        for interface in self.interfaces:
            if interface.header == header:
                self.interfaces.remove(interface)

    def find(self, header):
        for interface in self.interfaces:
            if interface.header == header:
                return interface
