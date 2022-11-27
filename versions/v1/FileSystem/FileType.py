import PyAsoka.asoka as a

from PyAsoka.FileSystem.File import File
from PyAsoka.GUI.Imports import AWidget
from PyAsoka.Processing.AProcess import AProcess, Headers, ProcessMessage
from PyAsoka.Instruments.AFile import File as OsFile


class FileType:
    def __init__(self, name: str, suffix: str, icon: str, handler, widgets=None):
        if widgets is None:
            widgets = {}
        self.name = name
        self.suffix = suffix
        self.icon = OsFile(icon)
        self.handler = handler
        self.widgets = widgets

    def __str__(self):
        return f'<FileType:{self.name}: {self.suffix}: {self.icon} {self.handler} {self.widgets.keys()}>'

    @staticmethod
    def create(name: str, suffixes, icon: str, handler, widgets: dict = None):
        if isinstance(suffixes, str):
            suffixes = [suffixes, ]
        for suffix in suffixes:
            filetype = FileType(name, suffix, icon, handler, widgets)
            if filetype.icon.exist():
                AProcess.send(Headers.FILE_TYPE_ADD, data=filetype)

    @staticmethod
    def fromSuffix(suffix):
        filetype = AProcess.request(Headers.FILE_TYPE_REQUEST, suffix, Headers.FILE_TYPE_REQUEST)
        if filetype is None:
            filetype = FileType('Неизвестный тип', suffix, f'{a.dir.images()}/notype.png', File)
        return filetype
