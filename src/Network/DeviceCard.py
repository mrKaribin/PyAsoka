from PyAsoka.Asoka import Asoka

import json


class DeviceCard:
    def __init__(self, name=None, _type=None, soft_type=None, local_ip=None, global_ip=None):
        self.name = name
        self.type = _type
        self.softType = soft_type
        self.localIp = local_ip
        self.globalIp = global_ip

    def toDict(self):
        return {
            'name': self.name,
            'type': self.type,
            'softType': self.softType,
            'localIp': self.localIp,
            'globalIp': self.globalIp
        }

    @staticmethod
    def fromDict(data):
        return DeviceCard(
            data.get('name'),
            data.get('type'),
            data.get('softType'),
            data.get('localIp'),
            data.get('globalIp')
        )

    @staticmethod
    def fromThisDevice():
        return DeviceCard(
            Asoka.Device.name,
            Asoka.Device.type,
            Asoka.Project.type,
            Asoka.Device.getLocalIP(),
            Asoka.Device.getGlobalIP()
        )
