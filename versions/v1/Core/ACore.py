import importlib
import os.path
import sys
import time

from PyAsoka.Processing.AProcess import *
from PyAsoka.Processing.ConnectorsManager import ConnectorsCoreManager
from PyAsoka.Core.ConnectorsMultiprocessManager import ConnectorsMultiprocessManager
from PyAsoka.Core.EventConnectorsManager import EventConnectorsManager
from PyAsoka.Core.Linguistics.AVoice import AVoice
from PyAsoka.Core.Linguistics.ASpeechRecognition import ASpeechRecognition
from PyAsoka.Core.WindowManager import WindowManager
from PyAsoka.Core.InterfaceManager import InterfaceManager, Interface
from PyAsoka.Connections.AEvent import AEvent
from PyAsoka.FileSystem.FileType import FileType
from Modules.NativeDialog.NativeDialog import NativeDialog

from threading import Timer
from PySide6.QtWidgets import QApplication


class ACoreId(Id):
    def __init__(self, id, name=None):
        if self.name is None:
            self.name = Id.DEFAULT_NAME
        self.id = id
        self.__unique_name__ = name


class Connector:
    def __init__(self, id: Id, process: ProcessCutaway):
        self.id = id
        self.process = process


class Action:
    def __init__(self, model, event_id, _type):
        self.model = model
        self.event_id = event_id
        self.type = _type


class ACore(AProcess):
    @staticmethod
    def init():
        if ACore.initialized:
            Log.warning("Попытка повторной инициализации ACore")
            return

        channel_main, channel_core = multiprocessing.Pipe()
        process_core = multiprocessing.Process(target=ACore.__core_init__, args=(channel_core,), name='CoreProcess')
        process_core.start()

        process = AProcess(channel_main, AProcess.Type.GUI)

        app = QApplication(sys.argv)

        manager = WindowManager()
        channel_main.send(ProcessMessage(Headers.WINDOW_MANAGER))
        while True:
            message = channel_main.recv()
            if message.header == Headers.WINDOW_MANAGER:
                ev_ow, ev_geh = message.data
                WindowManager.win_create.bind(manager.openWindow)
                a.connect(ev_ow, WindowManager.__open_window__)
                a.connect(ev_geh, WindowManager.__event_happened__)
                break
        process.create_window = ev_ow
        process.gui_connect = WindowManager.gui_connect

        return process, app, manager

    @classmethod
    def __core_init__(cls, channel):
        core = ACore(channel)
        core.run()

    def __init__(self, channel):
        ACore.initialized = True
        AProcess.current_process = self
        ACore.current_process = self

        self.name = multiprocessing.current_process().name
        self.ids = []
        self.active = True
        self.event_connectors = EventConnectorsManager()
        self.processes = [ProcessCutaway('', channel, AProcess.Type.GUI)]
        self.processes_limit = multiprocessing.cpu_count()
        self.threads = []
        self.thread_limit = 3
        self.tasks = []
        self.connectors = ConnectorsCoreManager()
        self.multi_connectors = ConnectorsMultiprocessManager()
        self.interfaces = InterfaceManager()
        self.actions = []
        self.filetypes = {}
        self.cycle_delay = 0.001
        self.voice = None
        self.listening = False
        self.listening_duration = 300.0
        self.listening_timer = None
        self.recognition = ASpeechRecognition()

        self.id = ACoreId(1, self.name)
        self.thread_connections = threading.Thread(target=self.connections, daemon=True)
        self.thread_connections.start()

        self.dialog = self.create_dialog()
        self.voice = AVoice(self.dialog)

        self.thread_listen = threading.Thread(target=self.listen, daemon=True)
        self.thread_listen.start()
        self.init_modules()
        self.create_window = None
        self.gui_event_happened = None
        Log.comment(f'ACore создан в процессе: {self.name}')

    def init_modules(self):
        self.find_module('Modules')

    def find_module(self, directory):
        files = os.listdir(directory)
        for file in files:
            arr = file.split('.')
            name = arr[0]
            ext = arr[1] if len(arr) > 1 else None
            # print(f'File: {file}, Extension: {ext}')
            if ext is None:
                # print(f'Path: {directory}/{file}')
                self.find_module(f'{directory}/{file}')
            elif ext == 'py':
                # print(f'Module: {directory}/{file}')
                module = importlib.import_module(f'{directory}/{name}'.replace('/', '.'), name)
                objects = dir(module)
                if 'asoka_init' in objects:
                    module.asoka_init()

    def create_dialog(self):  # ToDo убрать инициализацию модуля Лотос из ядра Асоки
        while True:
            for process in self.processes:
                if process._type_ == AProcess.Type.GUI and process.run is not None and self.create_window is not None:
                    time.sleep(0.05)
                    return NativeDialog()
                time.sleep(self.cycle_delay)

    def listen(self):
        from PyAsoka.src.Linguistics import APhraseModelParser as Model

        name = 'ева'
        hello_model = Model.parse(f'[N {name} [C окей привет здравствуй здорово [N ты [C тут здесь]] [N добрый [C день вечер утро]]]]')
        bye_model = Model.parse(f'[C пока забудь [L до скорого]]')
        off_model = Model.parse(f'[C выключись отключись [L сладких снов]]')
        # self.listening_start()
        while self.active:
            phrase = self.recognition.listen()
            text = phrase.text()
            if text == self.voice.last_phrase:
                continue

            if not self.listening and hello_model == phrase:
                self.voice.say('Привет, чем займемся?')
                self.listening_start()
                continue

            if self.listening:
                self.dialog.new_phrase(1, text)

                if bye_model == phrase:
                    self.voice.say('Если понадоблюсь, только позовите')
                    self.listening_stop()

                elif off_model == phrase:
                    self.close()

                for action in self.actions:
                    if action.model == phrase:
                        self.connect_to(action.event_id, [], {'action': action.model.keys})
                        self.listening_start()
                        continue
            del[phrase]

    def listening_start(self):
        if self.listening_timer is not None:
            self.listening_timer._cancel_()
        self.listening = True
        self.listening_timer = Timer(self.listening_duration, self.listening_stop)
        self.listening_timer.start()
        self.dialog._listening_(True)

    def listening_stop(self):
        self.listening = False
        self.listening_timer = None
        self.dialog._listening_(False)

    def connections(self):
        while self.active:
            for process in self.processes:
                if process.channel.poll():
                    message = process.channel.recv()
                    try:
                        self.__connections__(process, message)
                        self.__core_connections__(process, message)
                    except Exception as e:
                        Log.error(f'ACore.connections: Ошибка исполнения: {e}')

            time.sleep(self.cycle_delay)

    def __core_connections__(self, process: ProcessCutaway, message: ProcessMessage):
        header = message.header

        if header == Headers.NEW_ID:
            name = message.data
            process.channel.send(ProcessMessage(Headers.NEW_ID, self.create_id(name)))

        if header == Headers.WINDOW_MANAGER:
            ev_cw = AEvent('create_window', AEvent.Type.SYSTEM)
            ev_geh = AEvent('gui_event_happened', AEvent.Type.SYSTEM)
            process.channel.send(ProcessMessage(Headers.WINDOW_MANAGER, data=[ev_cw, ev_geh]))
            self.create_window = ev_cw
            self.gui_event_happened = ev_geh

        if header == Headers.REGISTRATION:
            process.name = message.cutaway.name
            process.close, process.run, process.kill = message.data

            ev_cp = AEvent('create_process', AEvent.Type.SYSTEM)
            a.connect(ev_cp, self.create_process)

            ev_rtiop = AEvent('run_task_in_other_process', AEvent.Type.SYSTEM)
            a.connect(ev_rtiop, self.run_task_in_process)

            ev_ow = AEvent('open_window', AEvent.Type.SYSTEM)
            if process.name != 'MainProcess':
                a.connect(ev_ow, self.create_window)

            ev_exiting = AEvent('exiting', AEvent.Type.SYSTEM)

            process.channel.send(ProcessMessage(
                Headers.REGISTRATION,
                cutaway=ProcessCutaway(multiprocessing.current_process().name, None, AProcess.Type.CORE),
                data={
                    'events': [
                        ev_cp, ev_rtiop, ev_ow, ev_exiting
                    ]
                }
            ))

        if header == Headers.CONNECTOR_ADDED:
            connector_id, connector_name = message.data
            self.multi_connectors.add(ACoreId(connector_id, connector_name), process)  # (connector_id, process)

        if header == Headers.CONNECTOR_REMOVED:
            connector_id, connector_name = message.data
            self.multi_connectors.remove(ACoreId(connector_id, connector_name))

        if header == Headers.INTERFACE_ADDED:
            _header = message.data
            self.interfaces.add(_header, process)

        if header == Headers.INTERFACE_REMOVED:
            _header = message.data
            self.interfaces.remove(_header)

        if header == Headers.EVENT_CONNECT:
            #  event_id, event_name, connector_id, connector_name = message.data
            #  self.connect(ACoreId(event_id, event_name), ACoreId(connector_id, connector_name))
            event_id, connector_id = message.data
            self.connect(event_id, connector_id)

        if header == Headers.EVENT_DISCONNECT:
            # event_id, event_name, connector_id, connector_name = message.data
            # self.disconnect(ACoreId(event_id, event_name), ACoreId(connector_id, connector_name))
            event_id, connector_id = message.data
            self.disconnect(event_id, connector_id)

        if header == Headers.EVENT_CONNECTION:
            id, args, kwargs = message.data
            self.connect_to(id, args, kwargs)

        if header == Headers.ACTION_ADD:
            model, _type, event_id = message.data
            self.add_action(model, event_id, _type)

        if header == Headers.ACTION_REMOVE:
            self.remove_action(message.data)

        if header == Headers.FILE_TYPE_ADD:
            self.add_filetype(message.data)

        if header == Headers.FILE_TYPE_REMOVE:
            self.remove_filetype(message.data)

        if header == Headers.FILE_TYPE_REQUEST:
            process.channel.send(ProcessMessage(
                Headers.FILE_TYPE_REQUEST, self.get_filetype(message.data), id=message._id_))

        if header == Headers.SAY_PHRASE:
            text, mode, priority, wait = message.data
            callback = None
            if wait:
                callback = lambda: process.channel.send(ProcessMessage(Headers.SAID_PHRASE))
            self.voice.say(text, mode, priority, False, callback)

        for interface in self.interfaces():
            if isinstance(interface, Interface) and header == interface.header:
                args, kwargs = message.data
                if interface.cutaway.name != self.name:
                    interface.cutaway.channel.send(ProcessMessage(Headers.INTERFACE_HAPPENED, [header, args, kwargs]))
                else:
                    interface.callback(*args, *kwargs)

    def connect_to(self, id, args, kwargs):
        from PyAsoka.Core.EventConnectorsManager import EventConnector
        from PyAsoka.Core.ConnectorsMultiprocessManager import ConnectorsCutaway
        if (event_connector := self.event_connectors.find(id)) is not None and isinstance(event_connector, EventConnector):
            for connector_id in event_connector.connectors_id:
                if (cutaway := self.multi_connectors.find(connector_id)) is not None and isinstance(cutaway, ConnectorsCutaway):
                    # print('Core connector: ', connector.process.name, args, kwargs)
                    if cutaway._process_.name == self.name:
                        self.to_connector(connector_id, args, kwargs)
                    else:
                        cutaway._process_.channel.send(ProcessMessage(Headers.EVENT_HAPPENED,
                                                                      data=[connector_id, args, kwargs]))
                    continue
                Log.warning(
                    f'Для события ({id()}) не найден коннектор ({connector_id}) в ядре. Не удалось соединить событие с обработчиком.')

    def generate_id(self, name=None):
        new_id = 2
        count = 0
        while True:
            free_id = True
            free_name = True
            for id in self.ids:
                if new_id == id():
                    free_id = False
                if name is not None and f'{name}{count if count != 0 else ""}' == id.name():
                    free_name = False
                if not free_id and not free_name:
                    break

            if not free_id:
                new_id += 1

            if not free_name:
                count += 1

            if free_id and free_name:
                return new_id, None if name is None else f'{name}{count if count != 0 else ""}'

    def create_id(self, name=None):
        id, name = self.generate_id(name)
        self.ids.append(ACoreId(id, name))
        return id, name

    def create_process(self):
        channel_proc, channel_core = multiprocessing.Pipe()
        self.processes.append(ProcessCutaway('', channel_core, AProcess.Type.SERVICE))
        process_core = multiprocessing.Process(target=lambda channel, proc_type: AProcess(channel, proc_type),
                                               args=(channel_proc, AProcess.Type.SERVICE))
        process_core.start()

    def run_task_in_process(self, task: Task, proc_type: AProcess.Type):
        for process in self.processes:
            if process._type_ == proc_type:
                process.run(task)

    def connect(self, event_id, connector_id):
        self.event_connectors.add(event_id, connector_id)

    def disconnect(self, event_id, connector_id=None):
        self.event_connectors.remove(event_id, connector_id)

    def create_interface(self, header: Headers, callback):
        self.interfaces.add(header, ProcessCutaway(self.name, None), callback)

    def remove_interface(self, header):
        self.interfaces.remove(header)

    def add_action(self, model, event_id, _type):
        self.actions.append(Action(model, event_id, _type))

    def remove_action(self, _id):
        for action in self.actions:
            if action.event_id == _id:
                self.actions.remove(action)
                return

    def add_filetype(self, filetype: FileType):
        if isinstance(filetype, FileType):
            self.filetypes[filetype.suffix] = filetype

    def remove_filetype(self, filetype: FileType):
        if isinstance(filetype, FileType):
            if filetype.suffix in self.filetypes.keys():
                self.filetypes.pop(filetype.suffix)

    def get_filetype(self, suffix):
        if suffix in self.filetypes.keys():
            return self.filetypes[suffix]
        else:
            return None

    def run(self):
        i = 0
        while self.active:
            i += 1
            time.sleep(self.cycle_delay)  # ToDo

    def say(self, text, mode=AVoice.SPEACH_NORMAL, priority=AVoice.PRIORITY_NORMAL, wait=False, callback=None, voice_set=None):
        if self.voice is not None:
            self.voice.say(text, mode, priority, wait, callback, voice_set)

    def close(self):
        self.voice.say('Пойду отдохну. До встречи', wait=True)
        for process in self.processes:
            process.channel.send(ProcessMessage(Headers.CLOSE))
        self.active = False
        self.kill()

    initialized = False
