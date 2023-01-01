from enum import Enum


class Asoka:

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
        _users_ = {'state': False}
        _speach_ = {'state': False}

        @staticmethod
        def enableUsers():
            Asoka.Modules._users_['state'] = True

        @staticmethod
        def enableSpeach(name, voice=None):
            Asoka.Modules.enableUsers()
            Asoka.Modules._speach_['name'] = name
            Asoka.Modules._speach_['voice'] = voice
            Asoka.Modules._speach_['state'] = True

    @staticmethod
    def initialization():
        from PyAsoka.src.Core.Core import Core
        from PyAsoka.GUI.Application import Application

        app = Application()
        core = Core()

        return core, app

    @staticmethod
    def core():
        from PyAsoka.src.Core.Core import core
        return core()

    @staticmethod
    def app():
        pass
