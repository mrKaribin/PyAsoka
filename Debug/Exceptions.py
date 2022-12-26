from PyAsoka.Debug.Logs import Logs


class UnsupportableType(Exception):
    pass


class Exceptions:

    @staticmethod
    def UnsupportableType(values):
        text = f'Получен некорректный тип данных: '
        for value in values:
            text += f' {type(value)}'
        Logs.error(text)
        raise UnsupportableType(text)

    class ObjectNotInitialized(Exception):
        pass
