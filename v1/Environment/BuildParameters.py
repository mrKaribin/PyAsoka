import json

from enum import Enum, auto


class BuildParameters:

    class Architecture:
        LINUX = 'LINUX'

    class System:
        MANJARO = 'MANJARO'

    def __init__(self, arch, system):
        self.architecture = arch
        self.system = system
