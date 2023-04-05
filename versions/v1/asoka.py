import os
from enum import Enum, auto
from random import randint

version = '1.0b'
comment = None
warning = None
error = None

nullInt = -1


class language(Enum):
    russian = auto()
    english = auto()


class GlobalDirectory:
    def __init__(self, pattern):
        self.pattern = pattern

    def __call__(self, *args, **kwargs):
        return self.pattern()

    def change(self, pattern):
        self.pattern = pattern()


class dir:
    path = GlobalDirectory(lambda: os.getcwd())
    asoka = GlobalDirectory(lambda: f'{os.getcwd()}/PyAsoka')
    log = GlobalDirectory(lambda: f'{dir.path()}/log.txt')
    images = GlobalDirectory(lambda: f'{dir.asoka()}/Icons')


class random:
    @staticmethod
    def int(minimum: int = 0, maximum: int = 1000000):
        return randint(minimum, maximum)

    @staticmethod
    def float(minimum: int, maximum: int, rng):
        minimum, maximum = minimum * 10 ** rng, maximum * 10 ** rng
        return randint(minimum, maximum) / (10 ** rng)

    @staticmethod
    def symbol(simbols='абвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890'):
        minimum, maximum = 0, len(simbols) - 1
        return simbols[randint(minimum, maximum)]

    @staticmethod
    def string(length=10, simbols='абвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890'):
        string = ''
        for i in range(length):
            string += random.symbol(simbols)
        return string

    @staticmethod
    def timepoint(year=None, month=None, day=None, hour=None, minute=None, second=None):
        from PyAsoka.src.Instruments.Timepoint import Timepoint
        if year is None:
            year = random.int(1, 3000)
        if month is None:
            month = random.int(1, 12)
        if day is None:
            day = random.int(1, 28)
        if hour is None:
            hour = random.int(0, 23)
        if minute is None:
            minute = random.int(0, 59)
        if second is None:
            second = random.int(0, 59)
        return Timepoint(year, month, day, hour, minute, second)


def getDatabasePassword(database_name):
    return 'topsecretpassword'


def say(text: str, mode: int = 0, priority: int = 1, wait: bool = False):
    from PyAsoka.Processing.AProcess import AProcess, ProcessMessage, Headers
    process = AProcess.current_process
    if process.name != 'CoreProcess':
        process.core.channel.send(ProcessMessage(Headers.SAY_PHRASE, (text, mode, priority, wait)))
        if wait:
            process.wait_for_message(process.core, Headers.SAID_PHRASE)
    else:
        from PyAsoka.Core.ACore import ACore
        ACore.current_process.voice.say(text, mode, priority, wait)


def connect(event, connector, _type=None, call_type=None):
    from PyAsoka.Connections.AConnector import AConnector, AEvent
    from PyAsoka.Processing.AProcess import AProcess, ProcessMessage, Headers, Id
    event_id, connector_id = 0, 0

    if isinstance(event, Id):
        event_id = event
    elif isinstance(event, AEvent):
        event_id = event.id

    if isinstance(connector, Id):
        connector_id = connector
    elif isinstance(connector, AConnector):
        connector_id = connector.id
    elif callable(connector):
        connector = AConnector(connector, _type=_type, call_type=call_type)
        connector_id = connector.id

    process = AProcess.current_process
    if process.name != 'CoreProcess':
        process.core.channel.send(ProcessMessage(Headers.EVENT_CONNECT, (event_id, connector_id)))  # event_id.__id__, event_id.__unique_name__, connector_id.__id__, connector_id.__unique_name__
    else:
        process.connect(event_id, connector_id)


def disconnect(event, connector):
    from PyAsoka.Connections.AConnector import AConnector, AEvent
    from PyAsoka.Processing.AProcess import AProcess, ProcessMessage, Headers, Id
    event_id, connector_id = 0, None

    if isinstance(event, Id):
        event_id = event
    elif isinstance(event, AEvent):
        event_id = event.id

    if isinstance(connector, Id):
        connector_id = connector
    elif isinstance(connector, AConnector):
        connector_id = connector.id

    process = AProcess.current_process
    if process.name != 'CoreProcess':
        process.core.channel.send(ProcessMessage(Headers.EVENT_DISCONNECT, (event_id, connector_id)))
    else:
        process.disconnectClient(event_id, connector_id)
