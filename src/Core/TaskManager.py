from PyAsoka.src.Core.AsyncTask import AsyncTask
from PyAsoka.src.Core.TaskLoop import TaskLoop, ProcessInstance, ProcessMessage, Headers
from PyAsoka.src.Core.Object import Object, Signal

from multiprocessing import Process
from multiprocessing.connection import Connection
from threading import Thread


class TaskInstance(Object):
    updated = Signal(list, dict)
    completed = Signal(list, dict)

    def __init__(self, _id, parent, process: ProcessInstance):
        super().__init__()
        self._id_ = _id
        self._parent_ = parent
        self._process_ = process
        self._on_update_ = None
        self._on_complete_ = None

    @property
    def parent(self):
        return self._parent_

    def __on_update_handle__(self, args: list, kwargs: dict):
        if self._on_update_ is not None:
            if self.parent is not None:
                args.insert(0, self.parent)
            self._on_update_(*args, **kwargs)

    def __on_complete_handle__(self, args, kwargs):
        if self._on_complete_ is not None:
            if self.parent is not None:
                args.insert(0, self.parent)
            self._on_complete_(*args, **kwargs)

    def onUpdate(self, callback):
        from PyAsoka.Asoka import Asoka
        if self._on_update_ is not None:
            self.updated.disconnect(self.__on_update_handle__)
        self.updated.connect(self.__on_update_handle__, Asoka.ConnectionType.QueuedConnection)
        self._on_update_ = callback

    def onComplete(self, callback):
        from PyAsoka.Asoka import Asoka
        if self._on_complete_ is not None:
            self.completed.disconnect(self.__on_complete_handle__)
        self.completed.connect(self.__on_complete_handle__, Asoka.ConnectionType.QueuedConnection)
        self._on_complete_ = callback


class TaskManager:
    def __init__(self, core):
        self._core_ = core
        self._processes_ = []
        self._tasks_ = {}

        self._listener_thread_ = Thread(target=self.processesListener)
        self._listener_thread_.start()

    @property
    def core(self):
        return self._core_

    @property
    def processes(self) -> list[ProcessInstance]:
        return self._processes_

    @property
    def tasks(self) -> dict[int, TaskInstance]:
        return self._tasks_

    def processesListener(self):
        from time import sleep
        from PyAsoka.Asoka import Asoka

        while True:
            for process in self.processes:
                if process.haveInput():
                    message = process.read()

                    if message.header == Headers.TASKS_COUNT:
                        process._tasks_number_ = message.data['number']

                    elif message.header == Headers.TASK_COMPLETED:
                        _id, args, kwargs = message.data['id'], message.data['args'], message.data['kwargs']
                        self.tasks[_id].completed.emit(args, kwargs)

                    elif message.header == Headers.TASK_UPDATED:
                        _id, args, kwargs = message.data['id'], message.data['args'], message.data['kwargs']
                        # print(f'Process {process.process.name} ({process.tasksNumber} tasks): Task {_id} updated with {args}, {kwargs}')
                        self.tasks[_id].updated.emit(args, kwargs)

            sleep(Asoka.defaultCycleDelay)

    def newProcess(self) -> ProcessInstance:
        instance = TaskLoop().start()
        self._processes_.append(instance)
        return instance

    def getFreeProcess(self):
        from PyAsoka.Asoka import Asoka
        for process in self.processes:
            if process.tasksNumber < Asoka.Async.maxThreads:
                return process

        return self.newProcess()

    def addTask(self, task: AsyncTask, parent=None):
        process = self.getFreeProcess()
        process.write(ProcessMessage(Headers.NEW_TASK, {'id': task.id, 'task': task}))

        instance = TaskInstance(task.id, parent, process)
        if task.haveUpdateHandler():
            instance.onUpdate(task.onUpdate)
        if task.haveCompleteHandler():
            instance.onComplete(task.onComplete)
        self.tasks[task.id] = instance
        return instance
