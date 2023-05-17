from PyAsoka.src.Core.AsyncTask import AsyncTask
from PyAsoka.src.Debug.Exceptions import Exceptions

from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from threading import Thread


class Headers:
    NEW_TASK = 'NewTask'
    TASK_COMPLETED = 'TaskComplete'
    TASK_UPDATED = 'TaskUpdated'
    TASKS_COUNT = 'TasksCount'


class ProcessMessage:
    def __init__(self, header: str, data: dict):
        self._header_ = header
        self._data_ = data

    @property
    def header(self):
        return self._header_

    @property
    def data(self):
        return self._data_


class ProcessInstance:
    def __init__(self, process: Process, connection: Connection):
        self._process_ = process
        self._connection_ = connection
        self._tasks_number_ = 0

    @property
    def process(self):
        return self._process_

    @property
    def connection(self):
        return self._connection_

    @property
    def tasksNumber(self):
        return self._tasks_number_

    def haveInput(self):
        return self.connection.poll()

    def read(self) -> ProcessMessage:
        message = self.connection.recv()
        if isinstance(message, ProcessMessage):
            return message
        else:
            raise Exception('Получены некоректные данные от дочернего процесса (type != ProcessMessage)')

    def write(self, message: ProcessMessage):
        if isinstance(message, ProcessMessage):
            self.connection.send(message)
        else:
            raise Exceptions.UnsupportableType(message)


class TaskInstance:
    def __init__(self, _id, task: AsyncTask, thread: Thread):
        self._id_ = _id
        self._task_ = task
        self._thread_ = thread

    @property
    def id(self):
        return self._id_

    @property
    def task(self):
        return self._task_

    @property
    def thread(self):
        return self._thread_


class TaskLoop:
    def __init__(self):
        self._process_: 'Process' = None
        self._connection_: 'Connection' = None
        self._tasks_ = []

    @property
    def connection(self):
        return self._connection_

    @property
    def tasks(self) -> list[TaskInstance]:
        return self._tasks_

    def start(self):
        connection, process_connection = Pipe()
        self._connection_ = process_connection
        self._process_ = Process(target=self.loop)
        self._process_.start()
        return ProcessInstance(self._process_, connection)

    def loop(self):
        from time import sleep
        from PyAsoka.Asoka import Asoka

        while True:
            if self.connection.poll():
                message = self.connection.recv()
                if not isinstance(message, ProcessMessage):
                    raise Exception('Получены некоректные данные от родительского процесса (type != ProcessMessage)')

                if message.header == Headers.NEW_TASK:
                    task: 'AsyncTask' = message.data['task']
                    task.setUpdateCallback(self.taskUpdated)
                    task.setCompleteCallback(self.taskCompleted)
                    thread = Thread(target=task.run)
                    instance = TaskInstance(message.data['id'], task, thread)
                    self.tasks.append(instance)
                    thread.start()
                    self.updateTasksNumber()

            for task in list(self.tasks):
                if isinstance(task, TaskInstance):
                    if not task.thread.is_alive():
                        task.thread.join()
                        self.tasks.remove(task)
                        self.updateTasksNumber()

            sleep(Asoka.defaultCycleDelay)

    def updateTasksNumber(self):
        self.connection.send(ProcessMessage(Headers.TASKS_COUNT, {'number': len(self.tasks)}))

    def taskUpdated(self, _id, args, kwargs):
        self.connection.send(ProcessMessage(Headers.TASK_UPDATED, {'id': _id, 'args': args, 'kwargs': kwargs}))

    def taskCompleted(self, _id, args, kwargs):
        self.connection.send(ProcessMessage(Headers.TASK_COMPLETED, {'id': _id, 'args': args, 'kwargs': kwargs}))



