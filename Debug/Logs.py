import datetime
from enum import auto, Enum


class Logs:

    class Modes(Enum):
        FILE = auto()
        DATABASE = auto()
        CONSOLE = auto()

    class Levels:
        ALL = 1
        WARNINGS = 2
        ERRORS = 3

    mode = Modes.CONSOLE
    level = Levels.ALL

    @staticmethod
    def init():
        pass

    @staticmethod
    def getTimeMark():
        now = datetime.datetime.now()
        return now.strftime("%d-%m-%y %H:%M:%S")  # ToDo

    @staticmethod
    def write(text, preline: bool = False, postline: bool = False):
        modes = Logs.Modes
        text = f'{Logs.getTimeMark()}: {text}'
        if preline:
            text = '\n' + text
        if postline:
            text = text + '\n'

        if Logs.mode == modes.CONSOLE:
            print(text)

    @staticmethod
    def message(text, preline: bool = False, postline: bool = False):
        if Logs.level <= Logs.Levels.ALL:
            Logs.write(text, preline, postline)

    @staticmethod
    def success(text, preline: bool = False, postline: bool = False):
        if Logs.level <= Logs.Levels.WARNINGS:
            text = f'\033[32m{text}\033[0m'
            Logs.write(text, preline, postline)

    @staticmethod
    def warning(text, preline: bool = False, postline: bool = False):
        if Logs.level <= Logs.Levels.WARNINGS:
            text = f'\033[33m{text}\033[0m'
            Logs.write(text, preline, postline)

    @staticmethod
    def error(text, preline: bool = False, postline: bool = False):
        if Logs.level <= Logs.Levels.ERRORS:
            text = f'\033[31mERROR: {text}\033[0m'
            Logs.write(text, preline, postline)

