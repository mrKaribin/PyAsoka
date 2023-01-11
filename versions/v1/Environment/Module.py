from enum import Enum, auto

from PyAsoka.src.Environment.Builder import Builder


class Package:

    class Type(Enum):
        SYSTEM = auto()
        PYTHON = auto()
        CUSTOM = auto()

    def __init__(self, params: Builder, _type, name, version: str = None, in_package: bool = True, script=None):
        self.params = params
        self.type = _type
        self.name = name
        self.version = version
        self.in_package = in_package
        self.script = script

    def create_install_script(self):
        if self.type == Package.Type.SYSTEM:
            from PyAsoka.src.Environment.SystemEnvironment import SystemEnvironment
            return SystemEnvironment.install_script(self)
        if self.type == Package.Type.PYTHON:
            from PyAsoka.src.Environment.PythonEnvironment import PythonEnvironment
            return PythonEnvironment.install_script(self)


class Module:
    def __init__(self, name):
        self.name = name

