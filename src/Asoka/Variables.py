

class Variables:

    @staticmethod
    def get(name: str):
        from PyAsoka.src.Instruments.Variable import Variable
        var = Variable.selector.filter(name=name).first()
        if var is not None:
            return var.getData()
        else:
            return None

    @staticmethod
    def set(name: str, data):
        from PyAsoka.src.Instruments.Variable import Variable
        var = Variable.selector.filter(name=name).first()
        if var is not None:
            var.setData(data)
            var.save()
        else:
            var = Variable(name=name)
            var.setData(data)
            var.save()

    @staticmethod
    def delete(name: str):
        from PyAsoka.src.Instruments.Variable import Variable
        var = Variable.selector.filter(name=name).first()
        if var is not None:
            var.delete()

