

class ObjectReference:
    def __init__(self):
        self.id = 0
        self.value = None

    def decode(self, value):
        self.id = value

    def encode(self):
        return self.id
