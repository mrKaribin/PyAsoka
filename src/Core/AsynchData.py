from PyAsoka.Asoka import Asoka
from time import sleep


class AsynchData:
    def __init__(self, value):
        self._value_ = value
        self._lock_ = False

    def __call__(self):
        self.__wait_unlock__()
        return self._value_

    def set(self, value):
        self.__wait_unlock__()
        self._value_ = value

    def lock(self):
        self.__wait_unlock__()
        self._lock_ = True
        return self._value_

    def unlock(self):
        self._lock_ = False

    def lockedTask(self, function, *args, **kwargs):
        self.lock()
        function(*args, **kwargs)
        self.unlock()

    def __wait_unlock__(self):
        while self._lock_:
            sleep(Asoka.defaultCycleDelay)
