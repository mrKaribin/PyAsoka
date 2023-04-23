from enum import IntEnum

import os


class Project:
    class Mode(IntEnum):
        RELEASE = 1
        TESTS = 2
        DEBUG = 3

    class Type(IntEnum):
        SERVER = 1
        LOCAL_SERVER = 2
        CLIENT = 3
        DEVICE = 4

    mode = Mode.RELEASE
    type = Type.CLIENT
    secret = 'asoka_secret_code'

    class Path:
        HOME = os.getcwd()
        MEDIA = '\\media'

        @staticmethod
        def Home():
            return Project.Path.HOME

        class Asoka:
            PATH = '\\PyAsoka'
            MEDIA = '\\media'
            MODELS = '\\models'
            DRIVERS = '\\drivers'

            @staticmethod
            def Path():
                Path = Project.Path
                return Path.HOME + Path.Asoka.PATH

            @staticmethod
            def Models():
                Path = Project.Path
                return Path.HOME + Path.Asoka.PATH + Path.Asoka.MODELS

            @staticmethod
            def Drivers():
                Path = Project.Path
                return Path.HOME + Path.Asoka.PATH + Path.Asoka.DRIVERS

            class Media:
                ICONS = '\\icons'
                IMAGES = '\\images'

                @staticmethod
                def Icons():
                    Path = Project.Path
                    return Path.HOME + Path.Asoka.PATH + Path.Asoka.MEDIA + Path.Asoka.Media.ICONS

                @staticmethod
                def Images():
                    Path = Project.Path
                    return Path.HOME + Path.Asoka.PATH + Path.Asoka.MEDIA + Path.Asoka.Media.IMAGES

        class Media:
            ICONS = '\\icons'
            IMAGES = '\\images'

            @staticmethod
            def Icons():
                Path = Project.Path
                return Path.HOME + Path.MEDIA + Path.Media.ICONS

            @staticmethod
            def Images():
                Path = Project.Path
                return Path.HOME + Path.MEDIA + Path.Media.IMAGES
