

class Interface:
    def __init__(self, header, callback):

        self.header = header
        self.callback = callback


class InterfaceManager:
    def __init__(self):
        self.interfaces = []

    def __call__(self, *args, **kwargs):
        return self.interfaces

    def add(self, header, callback):
        self.interfaces.append(Interface(header, callback))

    def remove(self, header):
        for interface in self.interfaces:
            if interface.header == header:
                self.interfaces.remove(interface)

    def find(self, header):
        for interface in self.interfaces:
            if interface.header == header:
                return interface
