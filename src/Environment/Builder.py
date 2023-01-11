import platform

from PyAsoka.src.Debug.Logs import Logs


class OSInfo:

    class Name:
        LINUX = 'Linux'
        Windows = 'Windows'
        MAC = 'Darwin'

    @classmethod
    def fromSystem(cls):
        info = OSInfo(platform.system())
        info.release = platform.release()
        info.version = platform.version()
        return info

    def __init__(self, name, release=None, version=None):
        self.name = name
        self.release = release
        self.version = version

    def __eq__(self, other):
        if isinstance(other, OSInfo):
            if self.name != self.name:
                return False
            if None not in (self.release, other.release) and self.release != other.release:
                return False
            if None not in (self.version, self.version) and self.version != other.version:
                return False
            return True
        else:
            Logs.exception_unsupportable_type(other)


class Builder:

    class OSType:
        LINUX = OSInfo(OSInfo.Name.LINUX)
        WINDOWS = OSInfo(OSInfo.Name.Windows)
        WINDOWS_10 = OSInfo(OSInfo.Name.Windows, '10')
        MAC = OSInfo(OSInfo.Name.MAC)

    @classmethod
    def fromSystem(cls):
        builder = Builder(OSInfo.fromSystem())
        return builder

    def __init__(self, os: OSInfo):
        self.os = os
