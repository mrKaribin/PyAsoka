from PyAsoka.GUI.Style import *


class Styles:
    @staticmethod
    def window():  # Обычные окна. Окно - виджет верхнего уровня
        return Style(background=Colors.Background.default(),
                     background_line=Colors.BackgroundLine.default(),
                     frame=Colors.Frame.default(),
                     line=Colors.Line.default(),
                     text=Colors.Text.default())

    @staticmethod
    def toolWindow():  # Полупрозрачные окна для работы в режиме оверлея
        return Style(frame=Color(90, 90, 90, 220),
                     background=Color(70, 70, 70, 220),
                     background_line=Color(100, 204, 204, 220),
                     line=Colors.Line.default(),
                     text=Colors.Text.default())

    @staticmethod
    def overlayFullscreen():  # Полупрозрачные окна для работы в режиме оверлея
        return Style(background=Colors.Background.blured(),
                     background_line=Colors.BackgroundLine.default(),
                     frame=Colors.Frame.focus(),
                     line=Colors.Line.default(),
                     text=Colors.Text.default())

    @staticmethod
    def widget():  # Стандартный виджет для любого уровня вложенности
        return Style(background=None,
                     background_line=Colors.BackgroundLine.default(),
                     frame=None,
                     line=Colors.Line.default(),
                     text=Colors.Text.default())

    @staticmethod
    def button():  # Стандартный виджет для любого уровня вложенности
        return Style(background=Colors.Background.active(),
                     background_line=Colors.BackgroundLine.default(),
                     frame=Colors.Frame.dark(),
                     line=Colors.Line.default(),
                     text=Colors.Text.default())

    @staticmethod
    def frameWidget():
        return Style(background=Color(80, 80, 80),
                     background_line=Colors.BackgroundLine.default(),
                     frame=Color(75, 75, 75),
                     line=Colors.Line.default(),
                     text=Colors.Text.default())

    @staticmethod
    def focusWidget():
        return Style(background=Colors.Background.default(),
                     background_line=Colors.BackgroundLine.default(),
                     frame=Colors.Frame.focus(),
                     line=Colors.Line.default(),
                     text=Colors.Text.default())

    @staticmethod
    def focusTextWidget():
        return Style(background=None,
                     background_line=Colors.BackgroundLine.default(),
                     frame=None,
                     line=Colors.Line.default(),
                     text=Colors.Text.focus())


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

