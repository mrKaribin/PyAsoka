from PyAsoka.Asoka import Asoka
from PyAsoka.Debug import Logs
from PyAsoka.src.Core.User import UsersManager
from PyAsoka.src.Core.CommunicationEngine import CommunicationEngine, SpeechEngine
from threading import Thread

import time


class Core:
    current = None

    def __init__(self):
        if self.current is not None:
            Logs.warning('Попытка повторной инициализации Application')
            return
        self.current = self

        self._threads_ = {}
        self._names_ = {}
        self._ids_ = {}

        self._current_user_ = None
        self._users_ = None

        self._communication_ = None

        self._thread_ = Thread(target=self.run)
        self._thread_.start()

    def getId(self, obj, name: str = None):
        _id, _name = None, None

        for i in range(2000000000):
            if self._ids_[i] is None:
                _id = i

        if self._names_[name] is None:
            _name = name

        self._ids_[_id] = obj
        self._names_[_name] = obj

        return _id, _name

    @property
    def communication(self) -> CommunicationEngine:
        return self._communication_

    def run(self):
        while True:
            users = Asoka.Modules._users_
            if users['state'] and self._users_ is None:
                self._users_ = UsersManager()
                self._current_user_ = self._users_.create('Демьян')

            speach = Asoka.Modules._speach_
            if speach['state'] and self._communication_ is None:
                name, voice = speach['name'], speach['voice']
                if voice is None:
                    voice = SpeechEngine.Voices.IVONA

                user = self._users_.create(name)
                self._communication_ = CommunicationEngine(user, voice)

            time.sleep(Asoka.defaultCycleDelay)


def core() -> Core:
    return Core.current
