from PyAsoka.GUI.AStyle import *


class Styles:
    @staticmethod
    def window():  # Обычные окна. Окно - виджет верхнего уровня
        return AStyle(background=Colors.Background.default(),
                      background_line=Colors.BackgroundLine.default(),
                      frame=Colors.Frame.default(),
                      line=Colors.Line.default(),
                      text=Colors.Text.default())

    @staticmethod
    def toolWindow():  # Полупрозрачные окна для работы в режиме оверлея
        return AStyle(frame=AColor(90, 90, 90, 220),
                      background=AColor(70, 70, 70, 220),
                      background_line=AColor(100, 204, 204, 220),
                      line=Colors.Line.default(),
                      text=Colors.Text.default())

    @staticmethod
    def overlayFullscreen():  # Полупрозрачные окна для работы в режиме оверлея
        return AStyle(background=Colors.Background.blured(),
                      background_line=Colors.BackgroundLine.default(),
                      frame=Colors.Frame.focus(),
                      line=Colors.Line.default(),
                      text=Colors.Text.default())

    @staticmethod
    def widget():  # Стандартный виджет для любого уровня вложенности
        return AStyle(background=None,
                      background_line=Colors.BackgroundLine.default(),
                      frame=None,
                      line=Colors.Line.default(),
                      text=Colors.Text.default())

    @staticmethod
    def button():  # Стандартный виджет для любого уровня вложенности
        return AStyle(background=Colors.Background.active(),
                      background_line=Colors.BackgroundLine.default(),
                      frame=Colors.Frame.dark(),
                      line=Colors.Line.default(),
                      text=Colors.Text.default())

    @staticmethod
    def frameWidget():
        return AStyle(background=AColor(80, 80, 80),
                      background_line=Colors.BackgroundLine.default(),
                      frame=AColor(75, 75, 75),
                      line=Colors.Line.default(),
                      text=Colors.Text.default())

    @staticmethod
    def focusWidget():
        return AStyle(background=Colors.Background.default(),
                      background_line=Colors.BackgroundLine.default(),
                      frame=Colors.Frame.focus(),
                      line=Colors.Line.default(),
                      text=Colors.Text.default())

    @staticmethod
    def focusTextWidget():
        return AStyle(background=None,
                      background_line=Colors.BackgroundLine.default(),
                      frame=None,
                      line=Colors.Line.default(),
                      text=Colors.Text.focus())


class Colors:

    class Background:
        @staticmethod
        def default():
            return AColor(70, 70, 70)

        @staticmethod
        def active():
            return AColor(60, 60, 60)

        @staticmethod
        def blured():
            return AColor(0, 0, 0, 120)

    class BackgroundLine:
        @staticmethod
        def default():
            return AColor(100, 204, 204)

    class Frame:
        @staticmethod
        def default():
            return AColor(80, 80, 80)

        @staticmethod
        def active():
            return AColor(70, 70, 70)

        @staticmethod
        def dark():
            return AColor(50, 50, 50)

        @staticmethod
        def focus():
            return AColor(215, 110, 0)

    class Line:
        @staticmethod
        def default():
            return AColor(255, 255, 255)

    class Text:
        @staticmethod
        def default():
            return AColor(175, 215, 250)

        @staticmethod
        def focus():
            return AColor(215, 110, 0)

    class Highlight:
        @staticmethod
        def default():
            return AColor(0, 168, 107)

