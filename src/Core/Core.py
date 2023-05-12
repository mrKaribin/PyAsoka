from PyAsoka.Debug import Logs
from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.Core.User import UsersManager
from PyAsoka.src.Core.CommunicationEngine import CommunicationEngine, SpeechEngine
from PyAsoka.src.Core.LogicObjectsManager import LogicObjectsManager
from PyAsoka.src.Core.TaskManager import TaskManager
from PyAsoka.src.Linguistics import APhraseModelParser as Model
from PyAsoka.src.Network.Socket.Client import ClientSocket

from threading import Thread
from multiprocessing import Process

from enum import IntEnum
import time


def testProcess():
    from time import sleep

    def memorySize():
        from types import ModuleType, FunctionType
        from PyAsoka.src.Debug.Memory import Memory

        total = 0
        print('Globals:')
        for name, value in globals().items():
            BLACKLIST = ModuleType, FunctionType
            if not isinstance(value, BLACKLIST):
                size = Memory.getObjectSize(value, Memory.Units.MEGABYTES, 2)
                print(f'{name} size: {size} Mb')
                total += size

        print('Locals:')
        for name, value in locals().items():
            BLACKLIST = ModuleType, FunctionType
            if not isinstance(value, BLACKLIST):
                size = Memory.getObjectSize(value, Memory.Units.MEGABYTES, 2)
                print(f'{name} size: {size} Mb')
                total += size

        print(f'Total size: {total:.3} Mb')

    sec = 0
    while True:
        # print(f'Секунд прошло {sec}')
        if sec == 5:
            memorySize()
        sleep(1)
        sec += 1


class Core(Object):
    _current_ = None

    initialized = Signal()

    class Initialization:
        _objects_ = []

        @staticmethod
        def addObject(obj):
            Core.Initialization._objects_.append(obj)

    class State(IntEnum):
        PREPARATION = 1
        READY = 2

    class Modules:
        @staticmethod
        def Users():
            return {
                'moduleName': 'users'
            }

        @staticmethod
        def Speach(name, voice=None, conversation_engine=None):
            if voice is None:
                voice = SpeechEngine.Voices.XENIA
            if conversation_engine is None:
                from PyAsoka.src.Core.ConversationEngine import ConversationEngine
                conversation_engine = ConversationEngine
            return {
                'moduleName': 'speach',
                'name': name,
                'voice': voice,
                'conversationEngine': conversation_engine,
                'requirements': ['users']
            }

        @staticmethod
        def Client(_type, **kwargs):
            if _type == 'TCPSocket':
                host, port = kwargs.get('host'), kwargs.get('port')
                return {
                    'moduleName': 'client',
                    'type': _type,
                    'host': host,
                    'port': port
                }

    class PhraseModels:
        class User:
            hello = Model.parse(f'[N ева [C окей привет здравствуй здорово [N ты [C тут здесь]] [N добрый [C день вечер утро]]]]')
            bye = Model.parse(f'[C пока забудь [L до скорого]]')

    def __init__(self, modules=None):
        super().__init__()
        if Core._current_ is not None:
            Logs.warning('Попытка повторной инициализации Core')
            return
        if modules is None:
            modules = {}
        Core._current_ = self

        self._modules_ = {}
        for module in modules:
            self._modules_[module['moduleName']] = module

        self._threads_ = {}
        self._objects_ = LogicObjectsManager()
        self._tasks_ = TaskManager(self)
        self._names_ = {}
        self._ids_ = {}
        self._state_ = Core.State.PREPARATION

        self._users_ = None
        self._communication_ = None
        self._client_ = None

        self.modulesInitialization()
        self._thread_ = Thread(target=self.run)
        self._thread_.start()

    @property
    def modules(self) -> dict:
        return self._modules_

    @property
    def objects(self) -> LogicObjectsManager:
        return self._objects_

    @property
    def tasks(self) -> TaskManager:
        return self._tasks_

    @property
    def state(self) -> State:
        return self._state_

    @property
    def users(self) -> UsersManager:
        if self._users_ is None and 'users' not in self.modules.keys():
            raise Exception(f'Попытка вызова модуля <Users>, хотя он не был добавлен в список модулей AsokaCore')
        return self._users_

    @property
    def communication(self) -> CommunicationEngine:
        if self._communication_ is None and 'speach' not in self.modules.keys():
            raise Exception(f'Попытка вызова модуля <Speach>, хотя он не был добавлен в список модулей AsokaCore')
        return self._communication_

    @property
    def client(self) -> ClientSocket:
        if self._communication_ is None and 'client' not in self.modules.keys():
            raise Exception(f'Попытка вызова модуля <Client>, хотя он не был добавлен в список модулей AsokaCore')
        return self._client_

    def modulesInitialization(self):
        for module in self.modules.values():
            requirements = module.get('requirements')
            if requirements is not None:
                for requirement in requirements:
                    if requirement not in self.modules.keys():
                        raise Exception(f'AsokaCore: Отсутствует модуль {requirement} от которого зависит модуль {module["moduleName"]}')

        if 'users' in self.modules.keys():
            self._users_ = UsersManager()

        if 'speach' in self.modules.keys():
            speach = self.modules['speach']
            name, voice, convEngine = speach.get('name'), speach.get('voice'), speach.get('conversationEngine')
            user = self.users.create(name)
            self._communication_ = CommunicationEngine(user, voice, convEngine)
            # self._communication_.speech.speaking.connect(self._communication_.conversation.spokePhrase)
            # self._communication_.recognized.connect(self._communication_.conversation.recognizedPhrase)

        if 'client' in self.modules.keys():
            client = self.modules['client']
            protocol = client.get('type')
            if protocol == 'TCPSocket':
                host, port = client.get('host'), client.get('port')
                self._client_ = ClientSocket(host, port)

    def initialization(self):
        from PyAsoka.Asoka import Asoka

        for obj in Core.Initialization._objects_:
            self._objects_.add(obj)

        if 'speach' in self.modules.keys():
            while not self.communication.recognition.ready:
                time.sleep(Asoka.defaultCycleDelay)
        self._state_ = Core.State.READY
        self.initialized.emit()

        self.process = Process(target=testProcess)
        self.process.start()

    def waitForReady(self):
        from PyAsoka.Asoka import Asoka
        while self._state_ != Core.State.READY:
            time.sleep(Asoka.defaultCycleDelay)

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

    def run(self):
        from PyAsoka.Asoka import Asoka
        self.initialization()
        while True:
            time.sleep(Asoka.defaultCycleDelay)

    def recognizedPhrase(self, phrase):
        print('Core: ', phrase.text())


def core() -> Core:
    return Core._current_
