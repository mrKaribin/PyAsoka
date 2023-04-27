class Exceptions:

    class UnsupportableType(Exception):
        def __init__(self, *values):
            text = f'Получен некорректный тип данных: '
            for value in values:
                text += f' {type(value)}'
            self.message = text

        def __str__(self):
            return self.message

    class ValueIsOutOfRange(Exception):
        def __init__(self, value, min_val, max_val):
            text = f'Значение {value} вне допустимого диапазона {min_val} < x < {max_val}'
            self.message = text

        def __str__(self):
            return self.message

    class ObjectNotInitialized(Exception):
        pass
