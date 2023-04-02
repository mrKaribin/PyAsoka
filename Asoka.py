import os.path
import platform

from PyAsoka.src.Instruments.Databases import Databases, DatabaseType

from enum import Enum, IntEnum, auto


class Asoka:
    class Project:
        class Mode(IntEnum):
            RELEASE = 1
            TESTS = 2
            DEBUG = 3

        class Type(IntEnum):
            SERVER = 1
            LOCAL_SERVER = 2
            CLIENT = 3
            DEVICE = 4

        mode = Mode.RELEASE
        type = Type.CLIENT

        class Path:
            HOME = os.getcwd()
            ASOKA = '/PyAsoka'
            ASOKA_MEDIA = '/PyAsoka/media'
            ASOKA_MODELS = '/PyAsoka/models'

            @staticmethod
            def asoka():
                Path = Asoka.Project.Path
                return Path.HOME + Path.ASOKA

            @staticmethod
            def asokaModels():
                Path = Asoka.Project.Path
                return Path.HOME + Path.ASOKA_MODELS

            @staticmethod
            def asokaMedia():
                Path = Asoka.Project.Path
                return Path.HOME + Path.ASOKA_MEDIA

    class Device:
        class Type(IntEnum):
            SERVICE_COMPUTER = 1
            PERSONAL_COMPUTER = 2
            PHONE = 3
            SMART_DEVICE = 4
            CUSTOM = 5

        class OS(IntEnum):
            UNKNOWN = 1
            WINDOWS = 2
            LINUX = 3

        @staticmethod
        def getLocalIP():
            from socket import gethostbyname, gethostname
            return gethostbyname(gethostname())

        @staticmethod
        def getGlobalIP():
            from stun import get_ip_info
            data = get_ip_info()
            return data[1] if len(data) == 3 else None

        @staticmethod
        def getOS():
            system = platform.system()
            if system == 'Windows':
                return Asoka.Device.OS.WINDOWS
            elif system == 'Linux':
                return Asoka.Device.OS.LINUX
            else:
                return Asoka.Device.OS.UNKNOWN

        name = platform.node()
        type = Type.PERSONAL_COMPUTER


    class Language(Enum):
        RUSSIAN = 'RUS'
        ENGLISH = 'ENG'

    class Results:
        def __init__(self, ok: bool = True, data: dict | None = None):
            self._ok_ = ok
            self._data_ = data
            if data is not None:
                self.__dict__.update(data)

        def correct(self):
            return self._ok_

        def incorrect(self):
            return not self._ok_

    defaultPassword = 'topsecretpassword'
    defaultCycleDelay = 0.05

    class Modules:
        class Users:
            active = False

            @staticmethod
            def enable():
                Asoka.Modules.Users.active = True

        class Speach:
            active = False
            voice = ''
            name = ''

            @staticmethod
            def enable(name, voice=None):
                Asoka.Modules.Speach.active = True
                Asoka.Modules.Speach.name = name
                Asoka.Modules.Speach.voice = voice

    DatabaseType = DatabaseType

    databases = Databases()

    @staticmethod
    def initialization(*args):
        if Asoka.Project.type in (Asoka.Project.Type.CLIENT, Asoka.Project.Type.LOCAL_SERVER):
            from PyAsoka.src.Core.Core import Core
            from PyAsoka.src.GUI.Application import Application

            app = Application()
            core = Core()

            return core, app
        else:
            from PyAsoka.src.Server.Core import Core

            host, port = args
            print('point1')
            core = Core(host, port)

            return core

    @staticmethod
    def core():
        if Asoka.Project.type in (Asoka.Project.Type.CLIENT, Asoka.Project.Type.LOCAL_SERVER):
            from PyAsoka.src.Core.Core import core
            return core()

    @staticmethod
    def app():
        pass


Asoka.databases.add(DatabaseType.SQLITE, 'asoka.db')
