from PyAsoka.Debug.Logs import Logs


class Application:
    current = None

    def __init__(self):
        if self.current is not None:
            Logs.warning('Попытка повторной инициализации Application')
            return
        self.current = self

        self._threads_ = {}
        self._names_ = {}
        self._ids_ = {}

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
