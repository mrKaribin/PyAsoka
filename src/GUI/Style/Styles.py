from PyAsoka.src.GUI.Style.Style import Style
from PyAsoka.src.GUI.Style.Colors import Colors, Color


class Styles:
    class Window(Style,
                 background=Colors.Background.default(),
                 background_line=Colors.BackgroundLine.default(),
                 frame=Colors.Frame.default(),
                 line=Colors.Line.default(),
                 text=Colors.Text.default()):
        pass

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

    # Стандартный виджет для любого уровня вложенности
    class Widget(Style,
                 background_line=Colors.BackgroundLine.default(),
                 line=Colors.Line.default(),
                 text=Colors.Text.default()):
        pass

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
