

class Serializer:
    def __init__(self, **kwargs):
        self.fields = kwargs

    def encode(self, obj):
        data = {}
        for key, necessary in self.fields.items():
            try:
                data[key] = getattr(obj, key)
            except Exception as e:
                if necessary:
                    raise Exception('Отсутствует обязательное поле')
        return data

    def decode(self, obj, data: dict):
        for key, necessary in self.fields.items():
            try:
                setattr(obj, key, data[key])
            except Exception as e:
                if necessary:
                    raise Exception('Отсутствует обязательное поле')
        return obj
