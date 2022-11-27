from PyAsoka.Environment.BuildParameters import BuildParameters
from PyAsoka.Environment.Module import Package
from PyAsoka.Instruments.AFile import File


class Builder:
    def __init__(self, path: str = None):
        self.path = path
        self.params = BuildParameters(path)
        self.script = ''

    def install_system_modules(self):
        file = File('system.env' if self.path is None else f'{self.path}/system.env')
        data = file.read_json()
        for lib in data.keys():
            package = Package(self.params, t)

