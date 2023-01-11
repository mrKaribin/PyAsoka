from PyAsoka.src.GUI.Style.Color import Color


class Colors:

    class Background:
        @staticmethod
        def default():
            return Color(70, 70, 70)

        @staticmethod
        def active():
            return Color(60, 60, 60)

        @staticmethod
        def blured():
            return Color(0, 0, 0, 120)

    class BackgroundLine:
        @staticmethod
        def default():
            return Color(100, 204, 204)

    class Frame:
        @staticmethod
        def default():
            return Color(80, 80, 80)

        @staticmethod
        def active():
            return Color(70, 70, 70)

        @staticmethod
        def dark():
            return Color(50, 50, 50)

        @staticmethod
        def focus():
            return Color(215, 110, 0)

    class Line:
        @staticmethod
        def default():
            return Color(255, 255, 255)

    class Text:
        @staticmethod
        def default():
            return Color(175, 215, 250)

        @staticmethod
        def focus():
            return Color(215, 110, 0)

    class Highlight:
        @staticmethod
        def default():
            return Color(0, 168, 107)