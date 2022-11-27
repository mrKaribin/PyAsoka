import PyAsoka.asoka as a

class


class AScript():
    def __init__(self, user=int(), name=str(), code=str(), id=int()):
        super().__init__(user=user, name=name, code=code, id=id)

    def run(self):
        from PyAsoka.Processing.AProcess import AProcess
        code = self.get_code()
        exec(code, {"AProcess": AProcess}, {})
