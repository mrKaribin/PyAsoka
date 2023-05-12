from PyAsoka.src.Core.AsyncTask import AsyncTask
from PyAsoka.src.Core.TaskLoop import TaskLoop, ProcessInstance, ProcessMessage, Headers

from multiprocessing import Process
from multiprocessing.connection import Connection


class TaskInstance:
    def __init__(self, _id, process: ProcessInstance):
        self._id_ = _id
        self._process_ = process


class TaskManager:
    def __init__(self, core):
        self._core_ = core
        self._processes_ = []

    @property
    def core(self):
        return self._core_

    @property
    def processes(self) -> list[ ProcessInstance ]:
        return self._processes_

    def processesListener(self):
        while True:
            for process in self.processes:
                if process.haveInput():
                    message = process.read()

                    if message.header == Headers.TASK_COMPLETE:


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

    def addTask(self, task: AsyncTask):
        task_id = id(task)
        process = self.getFreeProcess()
        process.write(ProcessMessage(Headers.NEW_TASK, {'id': task_id, 'task': task}))
        return TaskInstance(task_id, process)
