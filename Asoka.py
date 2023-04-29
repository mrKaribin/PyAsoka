from PyAsoka.src.Asoka.Databases import Databases, DatabaseType
from PyAsoka.src.Asoka.Account import Account
from PyAsoka.src.Asoka.Project import Project
from PyAsoka.src.Asoka.Variables import Variables
from PyAsoka.src.Asoka.Generate import Generate

from PySide6.QtCore import Qt
from cryptography.fernet import Fernet
from enum import Enum, IntEnum

import platform


class Asoka:
    AspectRatio = Qt.AspectRatioMode
    Alignment = Qt.AlignmentFlag
    ConnectionType = Qt.ConnectionType
    TextFlag = Qt.TextFlag
    Key = Qt.Key

    DatabaseType = DatabaseType

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

    Databases = Databases()
    Variables = Variables
    Generate = Generate
    Account = Account()
    Project = Project

    defaultPassword = 'topsecretpassword'
    defaultCycleDelay = 0.05

    @staticmethod
    def initialization(**args):
        if Asoka.Project.type in (Asoka.Project.Type.CLIENT, Asoka.Project.Type.LOCAL_SERVER):
            from PyAsoka.src.Core.Core import Core
            from PyAsoka.src.GUI.Application.Application import Application

            app = Application()
            core = Core(modules=args.get('core'))

            return core, app
        else:
            from PyAsoka.src.Server.Core import Core

            host, port = args.get('host'), args.get('port')
            if host is None:
                host = ''
            core = Core(host, port)

            return core

    @staticmethod
    def core():
        if Asoka.Project.type in (Asoka.Project.Type.CLIENT, Asoka.Project.Type.LOCAL_SERVER):
            from PyAsoka.src.Core.Core import core
            return core()
        else:
            from PyAsoka.src.Server.Core import core
            return core()

    @staticmethod
    def app():
        from PyAsoka.src.GUI.Application.Application import app
        return app()

    @staticmethod
    def encrypt(data):
        cipher = Fernet(Asoka.Project.secret)
        return cipher.encrypt(data)

    @staticmethod
    def decrypt(data):
        cipher = Fernet(Asoka.Project.secret)
        return cipher.decrypt(data)


Asoka.Databases.add(DatabaseType.SQLITE, 'asoka.db')
