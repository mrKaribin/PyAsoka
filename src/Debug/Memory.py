from types import ModuleType, FunctionType
from gc import get_referents
from enum import IntEnum

import os
import sys
import psutil


class Memory:
    class Units(IntEnum):
        BYTES = 1
        KILOBYTES = 1024
        MEGABYTES = 1024 * 1024
        GIGABYTES = 1024 * 1024 * 1024

    @staticmethod
    def convert(value, from_type: Units, to_type: Units, accuracy=None):
        value = value * int(from_type) / int(to_type)
        if accuracy is not None:
            value = round(value, accuracy)
        return value

    @staticmethod
    def getObjectSize(obj, to_type: Units = Units.BYTES, accuracy=None):
        BLACKLIST = type, ModuleType, FunctionType
        """sum size of object & members."""
        if isinstance(obj, BLACKLIST):
            raise TypeError('getsize() does not take argument of type: ' + str(type(obj)))
        seen_ids = set()
        size = 0
        objects = [obj]
        while objects:
            need_referents = []
            for obj in objects:
                if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                    seen_ids.add(id(obj))
                    size += sys.getsizeof(obj)
                    need_referents.append(obj)
            objects = get_referents(*need_referents)

        if to_type != Memory.Units.BYTES:
            size = Memory.convert(size, Memory.Units.BYTES, to_type, accuracy)

        return size

    class RAM:

        class System:
            @staticmethod
            def total(to_type=None, accuracy=None):
                if to_type is None:
                    to_type = Memory.Units.MEGABYTES
                if accuracy is None:
                    accuracy = 1
                return Memory.convert(psutil.swap_memory().total, Memory.Units.BYTES, to_type, accuracy)

            @staticmethod
            def used(to_type=None, accuracy=None):
                if to_type is None:
                    to_type = Memory.Units.MEGABYTES
                if accuracy is None:
                    accuracy = 1
                return Memory.convert(psutil.swap_memory().used, Memory.Units.BYTES, to_type, accuracy)

            @staticmethod
            def percent():
                return psutil.swap_memory().percent

        @staticmethod
        def used(to_type=None, accuracy=None):
            if to_type is None:
                to_type = Memory.Units.BYTES
            return Memory.convert(psutil.Process(os.getpid()).memory_info().rss, Memory.Units.BYTES, to_type, accuracy)
