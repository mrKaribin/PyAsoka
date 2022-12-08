import PyAsoka.asoka as a
import PyAsoka.Instruments.Log as Log

import threading
import multiprocessing
import time

from PyAsoka.Core.Id import Id
from PyAsoka.Processing.ConnectorsManager import ConnectorsProcessManager
from PyAsoka.Processing.InterfaceManager import InterfaceManager
from multiprocessing.connection import Connection
from enum import Enum, auto


class Header:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Header):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        else:
            Log.exception_unsupportable_type(type(other))


class Headers:
    REGISTRATION = Header('REGISTRATION')
    WINDOW_MANAGER = Header('WINDOW_MANAGER')
    NEW_ID = Header('NEW_ID')
    EVENT_CONNECT = Header('EVENT_CONNECT')
    EVENT_DISCONNECT = Header('EVENT_DISCONNECT')
    CONNECTOR_ADDED = Header('CONNECTOR_ADDED')
    CONNECTOR_REMOVED = Header('CONNECTOR_REMOVED')
    INTERFACE_ADDED = Header('INTERFACE_ADDED')
    INTERFACE_REMOVED = Header('INTERFACE_REMOVED')
    INTERFACE_HAPPENED = Header('INTERFACE_HAPPENED')
    EVENT_CONNECTION = Header('EVENT_CONNECTION')
    EVENT_HAPPENED = Header('EVENT_HAPPENED')
    ACTION_ADD = Header('ACTION_ADD')
    ACTION_REMOVE = Header('ACTION_REMOVE')
    FILE_TYPE_ADD = Header('FILE_TYPE_ADD')
    FILE_TYPE_REMOVE = Header('FILE_TYPE_REMOVE')
    FILE_TYPE_REQUEST = Header('FILE_TYPE_REQUEST')

    SAY_PHRASE = Header('SAY_PHRASE')
    SAID_PHRASE = Header('SAID_PHRASE')

    DATABASE_TAKE = Header('DATABASE_TAKE')
    DATABASE_FREE = Header('DATABASE_FREE')

    CLOSE = Header('CLOSE')


class Status(Enum):
    OK = auto()


class ProcessCutaway:
    def __init__(self, name: str, channel: Connection, proc_type=None):
        if proc_type is None:
            proc_type = AProcess.Type.CUSTOM
        self.name = name
        self.type = proc_type
        self.channel = channel
        self.close = None
        self.run = None
        self.destroy = None

    def __eq__(self, other):
        if isinstance(other, ProcessCutaway):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        else:
            Log.exception_unsupportable_type(type(other))


class ProcessMessage:
    def __init__(self, header: Header, data=None, status: Status = Status.OK, cutaway: ProcessCutaway = None, id: Id = None):
        self.header = header
        self.cutaway = cutaway
        self.status = status
        self.data = data
        self.id = id
        self.__sender__ = None

    def set_sender(self, sender: ProcessCutaway):
        self.__sender__ = sender

    def sender(self):
        return self.__sender__


class Task:
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def exec(self):
        if self.args is None and self.kwargs is None:
            thread = threading.Thread(target=self.function, daemon=True)
        else:
            thread = threading.Thread(target=self.function, args=self.args, kwargs=self.kwargs, daemon=True)
        thread.start()
        return thread


class Request:
    def __init__(self, header: Header):
        self.id = Id()
        self.header = header


class AProcess:

    class Type(Enum):
        CORE = auto()
        GUI = auto()
        SERVICE = auto()
        CUSTOM = auto()

    class APIException(Exception):
        pass

    @classmethod
    def create(cls):
        if AProcess.current_process is not None:
            AProcess.create_process()
        else:
            Log.warning(f'Не удалось создать новый процесс из процесса {multiprocessing.current_process().name}. AProcess не инициализирован в текущем процессе')

    def __init__(self, core_channel, proc_type):
        self.name = multiprocessing.current_process().name
        self.type = proc_type
        self.core = ProcessCutaway('', None, AProcess.Type.CORE)
        self.active = True
        self.thread_limit = 3
        self.processes = []
        self.tasks = []
        self.threads = []
        self.messages = []
        self.requests = []
        self.replies = []
        self.connectors = ConnectorsProcessManager()
        self.interfaces = InterfaceManager()
        self._new_id_ = None
        self.cycle_delay = 0.02 if self.type == AProcess.Type.GUI else 0.001
        AProcess.current_process = self

        self.thread_connections = threading.Thread(target=self.connections, daemon=True)
        self.thread_connections.start()
        if not self.connect_to_core(core_channel):
            del self
            return

        self.id = Id(self.name)
        self.thread_run = threading.Thread(target=self.run, daemon=True)
        self.thread_run.start()
        Log.comment(f'Создан новый процесс: {self.name}')

    def connect_to_core(self, channel):
        from PyAsoka.Connections.AEvent import AEvent
        self.core.channel = channel

        ev_close = AEvent(f'{self.name}_process_close', AEvent.Type.SYSTEM)
        a.connect(ev_close, self.close)

        ev_run = AEvent(f'{self.name}_process_run', AEvent.Type.SYSTEM)
        a.connect(ev_run, self.add_task)

        ev_kill = AEvent(f'{self.name}_process_kill', AEvent.Type.SYSTEM)
        a.connect(ev_kill, self.kill)

        channel.send(ProcessMessage(Headers.REGISTRATION, data=(ev_close, ev_run, ev_kill), cutaway=ProcessCutaway(self.name, None, self.type)))
        reply = channel.recv()
        if reply.status == Status.OK:
            self.core.name = reply.cutaway.name
            self.create_process, self.run_task_in_process, self.create_window, self.exit = reply.data['events']
            return True
        else:
            self.core.channel = None
            return False

    def connections(self):
        while self.active:
            for process in [self.core, ] + self.processes:
                if process.channel is not None and process.channel.poll():
                    message = process.channel.recv()
                    message.set_sender(process)
                    for request in self.requests:
                        if message.header == request.header:
                            self.replies.append(message)
                            continue
                    self.messages.append(message)

            while len(self.messages) != 0:
                message = self.messages.pop()
                process = message.sender()
                try:
                    self.__connections__(process, message)
                    self.__process_connections__(process, message)
                except Exception as e:
                    Log.error(f'AProcess.connections: Ошибка исполнения: {e}')

            time.sleep(self.cycle_delay)

    # Тут описаны сообщения обрабатываемые и вторичными процессами и процессом ядра
    def __connections__(self, process: ProcessCutaway, message: ProcessMessage):
        header = message.header

        if header == Headers.EVENT_HAPPENED:
            id, args, kwargs = message.data
            self.to_connector(id, args, kwargs)

    # Тут описаны только сообщения обрабатываемые вторичными процессами
    def __process_connections__(self, process: ProcessCutaway, message: ProcessMessage):
        header = message.header

        if header == Headers.CLOSE:
            self.close()

        if header == Headers.NEW_ID:
            self._new_id_ = message.data

        if header == Headers.INTERFACE_HAPPENED:
            _header, args, kwargs = message.data
            for interface in self.interfaces():
                if interface.header == _header:
                    if self.type == AProcess.Type.GUI:
                        self.gui_connect(interface.callback, args, kwargs)
                    else:
                        interface.callback(*args, **kwargs)

    def create_id(self, name=None):
        self.core.channel.send(ProcessMessage(Headers.NEW_ID, name))
        while self._new_id_ is None:
            time.sleep(0.02)
        _id = self._new_id_
        self._new_id_ = None
        return _id

    def connect_to(self, id, args, kwargs):
        self.core.channel.send(ProcessMessage(Headers.EVENT_CONNECTION, [id, args, kwargs]))

    def to_connector(self, id, args, kwargs):
        if (connector := self.connectors.find(id)) is not None:
            connector.__happened__(args, kwargs)
        else:
            Log.warning(f'Не найден коннектор (id = {id()}) в процессе <{self.name}>. Не удалось соединить.')

    def run(self):
        while self.active:
            try:
                for thread in self.threads:
                    if not thread.is_alive():
                        thread.join()
                        self.threads.remove(thread)

                self.exec()
                time.sleep(self.cycle_delay)
            except Exception as e:
                Log.error(f'Ошибка исполнения в процессе {self.name}: {str(e)}')

    def event_happened(self, function, process_name):
        for process in [self.core, ] + self.processes:
            if process.name == process_name:
                process.channel.send(ProcessMessage(Headers.EVENT_HAPPENED, function))
                return True
        Log.warning(f'Не удалось отправить событие в процесс {process_name}. Процесс не найден.')
        return False

    def close(self):
        self.active = False
        self.kill()

    def kill(self):
        Log.comment(f'Уничтожение процесса: {self.name}')
        if self.name == 'MainProcess':
            self.gui_connect(self.kill_gui, [], {})
        else:
            exit()

    def kill_gui(self):
        from PySide6.QtWidgets import QApplication
        from PyAsoka.GUI.Widgets.AWidget import AWidget
        from threading import Timer

        for widget in QApplication.allWidgets():
            if widget.parent() is None:
                if isinstance(widget, AWidget):
                    # widget.vanishing()
                    widget.hide(1000)
                else:
                    widget.hide()
        timer = Timer(2.0, lambda: QApplication.exit())
        timer.start()

    @staticmethod
    def current():
        process = AProcess.current_process
        if process is None:
            raise Exception('Объект процесса не создан')
        else:
            if isinstance(process, AProcess):
                return process
            else:
                raise Exception('Объект процесса фальсифицирован')

    @staticmethod
    def add_task(_type, task, *args, **kwargs):
        process = AProcess.current()
        if _type == AProcess.Type.CUSTOM or (_type != AProcess.Type.GUI and _type == process.type):
            if isinstance(task, Task):
                process.tasks.append(task)
            elif callable(task):
                process.tasks.append(Task(task, *args, **kwargs))
        if process.type == AProcess.Type.GUI and _type == AProcess.Type.GUI:
            if isinstance(task, Task):
                process.gui_connect(task.function, task.args, task.kwargs)
            elif callable(task):
                process.gui_connect(task, args, kwargs)

    @staticmethod
    def create_interface(header: Headers, callback):
        process = AProcess.current()
        process.interfaces.add(header, callback)
        process.core.channel.send(ProcessMessage(Headers.INTERFACE_ADDED, header))

    @staticmethod
    def remove_interface(header):
        process = AProcess.current()
        process.interfaces.remove(header)
        process.core.channel.send(ProcessMessage(Headers.INTERFACE_REMOVED, header))

    @staticmethod
    def interface(header, *args, **kwargs):
        process = AProcess.current()
        process.core.channel.send(ProcessMessage(header, data=[args, kwargs]))

    @staticmethod
    def send(header, data):
        process = AProcess.current()
        process.core.channel.send(ProcessMessage(header, data))

    @staticmethod
    def request(header, data, response_header):
        process = AProcess.current()
        request = Request(response_header)
        process.requests.append(request)
        process.core.channel.send(ProcessMessage(header, data=data, id=request.id))
        return process.wait_for_message(process.core, request)

    @staticmethod
    def wait_for_message(sender: ProcessCutaway, request: Request):
        process = AProcess.current()
        if isinstance(request, Request):
            while True:
                for message in process.replies:
                    if message.sender() == sender and message.header == request.header and message.id == request.id:
                        process.replies.remove(message)
                        return message.data
        else:
            Log.exception_unsupportable_type(type(request))

    @staticmethod
    def exec():
        process = AProcess.current()
        if len(process.threads) < process.thread_limit:
            if len(process.tasks) != 0:
                process.threads.append(process.tasks.pop().exec())


    gui_connect = None
    current_process = None
    create_process = None
    run_task_in_process = None
    create_window = None
    exit = None
