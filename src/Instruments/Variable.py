from PyAsoka.src.MVC.Model.Model import Model
from PyAsoka.src.Instruments.Unitype import Unitype
from PyAsoka.Asoka import Asoka


class Variable(Model, profile=Asoka.Databases.asoka):
    name = Model.StrField().UNIQUE()
    data = Model.BinaryField()

    def setData(self, data):
        self.data = Asoka.encrypt(Unitype(data).toBytes())

    def getData(self):
        return Unitype.fromBytes(Asoka.decrypt(self.data)).decode()
