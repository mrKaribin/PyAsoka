from PyAsoka.src.Environment.Builder import Builder
from PyAsoka.src.Environment.Package import Package
from PyAsoka.src.Instruments.File import File


class Builder:
    def __init__(self, path: str = None):
        self.path = path
        self.params = Builder(path)
        self.script = ''

    def install_system_modules(self):
        file = File('system.env' if self.path is None else f'{self.path}/system.env')
        data = file.read_json()
        for lib in data.keys():
            package = Package(self.params, t)

