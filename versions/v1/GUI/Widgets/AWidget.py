from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from PySide6.QtGui import QPaintEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Property, QPoint, QRect, QSize
from PyAsoka.GUI.Styles import Styles, Style, Color
from PyAsoka.src.GUI.API.Screen import Screen
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.GUI.AnimationManager import AnimationManager, Animation

from threading import Timer


class AWidgetState:
    def __init__(self):
        self.drawers = []

    def add(self, drawer):
        self.drawers.append(drawer)

    def remove(self, drawer):
        self.drawers.remove(drawer)


class AWidgetStateManager:
    def __init__(self):
        self.states = {}
        self.active = {}

    def __getitem__(self, item):
        return self.states[item]

    def add(self, name, drawers):
        if name not in self.states.keys():
            self.states[name] = AWidgetState()
        if not isinstance(drawers, list):
            drawers = [drawers, ]

        for drawer in drawers:
            self.states[name].add(drawer)

        return self

    def remove(self, name):
        self.states.pop(name)
        return self

    def enable(self, name):
        if name in self.states.keys():
            self.active[name] = self.states[name]

    def disable(self, name):
        if name in self.active.keys():
            self.active.pop(name)


class AWidget(QWidget):
    class State:
        PREPARATION = 'LOADING'
        DEFAULT = 'LOADING'

    def __init__(self, parent: QWidget = None, movable: bool = False, clickable: bool = False, keyboard: bool = False,
                 geometry: tuple = None, style: Style = None, animated: bool = True, with_super: bool = True,
                 frame_size: int = 2, round_size: int = 20):
        if with_super:
            super().__init__(parent)

        if parent is not None:
            pass

        # public
        self.style = (Styles.window() if parent is None else Styles.widget()) if style is None else style
        self.colors = Style(self.style)
        self.states = AWidgetStateManager()\
            .add(self.State.PREPARATION, self.renderLoader) \
            .add(self.State.DEFAULT, self.renderBackground)
        self.movable = movable
        self.clickable = clickable
        self.animated = animated

        # private
        self._draw_content_ = True
        self._opacity_ = 1.0
        self._default_opacity_ = 1.0
        self._frame_size_ = frame_size
        self._round_size_ = round_size
        self._last_mouse_pos_ = None
        self._moved_by_mouse_ = False
        self._animation_opacity_ = AnimationManager()
        self._animations_color_ = AnimationManager()
        self._animations_geometry_ = AnimationManager()
        self._initialization_timer_ = Timer(0.05, self.__preparation__)

        # signals
        self.clicked = Signal(QWidget)
        self.resized = Signal(QRect)
        self.destroyed = Signal(QWidget)

        # class preparation
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        if self.parent() is None:
            self.setWindowFlag(Qt.WindowType.BypassWindowManagerHint)
            self.setWindowFlag(Qt.WindowType.WindowOverridesSystemGestures)
        if keyboard:
            self.setFocusPolicy(Qt.StrongFocus)
        else:
            self.setFocusPolicy(Qt.NoFocus)
        if geometry is not None:
            if isinstance(geometry, tuple) or isinstance(geometry, list):
                self.setGeometry(QRect(*geometry), duration=None)
            if isinstance(geometry, QRect):
                self.setGeometry(geometry, duration=None)
        self.colors.changed.bind(self.repaint)
        self.states.enable(self.State.DEFAULT)

    def initialization(self):
        self._initialization_timer_.start()

    def __preparation__(self):
        self.states.disable(self.State.DEFAULT)
        self.states.enable(self.State.PREPARATION)
        self.preparation()
        self.states.disable(self.State.PREPARATION)
        self.states.enable(self.State.DEFAULT)

    def preparation(self):
        pass

    def setOpacity(self, level, duration=None, anim_type=Animation.Type.QUEUE, autorun=True):
        if duration is not None:
            animation = Animation(self, b"alpha")
            animation.setStartValue(self.alpha)
            animation.setEndValue(level)
            animation.setDuration(duration)
            self._animation_opacity_.add(animation, anim_type)
            if autorun:
                self._animation_opacity_.start()
            return animation
        else:
            self.alpha = level

    def setColor(self, color: QColor, value: QColor, duration=None, anim_type=Animation.Type.QUEUE, autorun=True):
        if duration is not None:
            animation = Animation(color, b'color')
            animation.setStartValue(color.color if isinstance(color, Color) else color)
            animation.setEndValue(value.color if isinstance(color, Color) else value)
            animation.setDuration(duration)
            if autorun:
                self._animations_color_.add(animation, anim_type)
                self._animations_color_.start()
            return animation
        else:
            color = value

    def __emerging_default__(self):
        animation = self.show()
        return animation

    def __emerging_optional__(self, to_pos: QRect, from_point: QPoint):
        if to_pos is None:
            to_pos = self.geometry()
        if from_point is None:
            size = Screen(0).getSize()
            from_point = QPoint(size.width() // 2 - 20, size.height() - 20)

        step1 = QRect(from_point, QSize(40, 40))
        step2 = QRect(from_point.x(), to_pos.y(), 40, 40)
        step3 = QRect(to_pos.x(), to_pos.y(), 40, 40)

        self.visibleContent(False)
        self.setGeometry(step1, duration=None)
        self.setGeometry(step2, duration=200)
        self.setGeometry(step3, _from=step2, duration=300)
        self.setGeometry(to_pos, _from=step3, duration=300).ended.bind(lambda: self.visibleContent(True))
        return self._animations_geometry_

    def emerging(self, *args):
        if len(args) == 0:
            animation = self.__emerging_default__()
        else:
            animation = self.__emerging_optional__(*args)
        QWidget.show(self)
        return animation

    def __vanishing_default__(self):
        animation = self.hide()
        return animation

    def __vanishing_optional__(self, to_point: QPoint):
        if to_point is None:
            size = Screen(0).getSize()
            to_point = QPoint(size.width() // 2 - 20, size.height() - 20)

        step1 = QRect(self.pos().x(), to_point.y(), 40, 40)
        step2 = QRect(to_point, QSize(40, 40))

        self.visibleContent(False)
        self.setGeometry(self.geometry(), step1, duration=200)
        animation = self.setGeometry(step1, step2, duration=200)
        return animation

    def vanishing(self, *args):
        if len(args) == 0:
            animation = self.__vanishing_default__()
        else:
            animation = self.__vanishing_optional__(*args)
        animation.ended.bind(self.deleteLater)
        return animation

    def show(self, duration=250):
        if duration is not None:
            self.alpha = 0
            animation = self.setOpacity(self._default_opacity_, duration, Animation.Type.PARALLEL)
            super().show()
            self.activateWindow()
            return animation
        else:
            super().show()

    def hide(self, duration=250):
        if duration is not None:
            animation = self.setOpacity(0, duration, Animation.Type.PARALLEL)
            animation.ended.bind(super().hide)
            return animation
        else:
            super().hide()

    def setDefaultOpacity(self, value: float):
        self._default_opacity_ = value

    def visibleContent(self, state: bool):
        self._draw_content_ = state

    def move(self, _to: QPoint, duration=None, anim_type=Animation.Type.QUEUE, autorun=True):
        if duration is not None:
            animation = Animation(self, b'geometry')
            animation.setStartValue(self.geometry())
            animation.setEndValue(QRect(_to, self.size()))
            animation.setDuration(duration)
            if autorun:
                self._animations_geometry_.add(animation, anim_type).start()
            else:
                self._animations_geometry_.add(animation, anim_type)
            return animation
        else:
            QWidget.move(self, _to)

    def setGeometry(self, _to: QRect, _from: QRect = None, duration=None, anim_type=Animation.Type.QUEUE, autorun=True):
        if duration is not None:
            animation = Animation(self, b'geometry')
            animation.setStartValue(self.geometry() if _from is None else _from)
            animation.setEndValue(_to)
            animation.setDuration(duration)
            if autorun:
                self._animations_geometry_.add(animation, anim_type).start()
            else:
                self._animations_geometry_.add(animation, anim_type)
            return animation
        else:
            QWidget.setGeometry(self, _to)

    def enterEvent(self, event):
        if self.animated and self.parent() is None and self.style.background is not None and self.style.background.alpha() < 255:
            color = Color(self.colors.background)
            color.setAlpha(255)
            self.setColor(self.colors.background, color, 200, Animation.Type.PARALLEL)

    def leaveEvent(self, event):
        if self.animated and self.parent() is None and self.style.background is not None and self.style.background.alpha() < 255:
            self.setColor(self.colors.background, self.style.background, 200, Animation.Type.PARALLEL)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resized(self.geometry())

    def __get_painter__(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        parent = self.parent()
        if parent is None:
            painter.setCompositionMode(painter.CompositionMode_DestinationOver)
        elif issubclass(type(parent), AWidget) and (
                parent.colors.background is None or parent.colors.background.alpha() != 255):
            painter.setCompositionMode(painter.CompositionMode_SourceOver)
        else:
            painter.setCompositionMode(painter.CompositionMode_SourceIn)
        return painter

    def __is_content_visible__(self):
        return self.parent() is None or (self.parent() is not None and self.parent()._draw_content_)

    def renderLoader(self, event: QPaintEvent):
        pass

    def renderBackground(self, event: QPaintEvent):
        if self.__is_content_visible__():
            if self.colors.frame is not None or self.colors.background is not None:
                painter = self.__get_painter__()
                pen_size = self._frame_size_
                if self.colors.frame is not None:
                    painter.setPen(QPen(self.colors.frame, pen_size))
                else:
                    painter.setPen(QPen(self.colors.background, pen_size))
                if self.colors.background is not None:
                    painter.setBrush(QBrush(self.colors.background))
                indent = int(pen_size * 1.5)
                painter.drawRoundedRect(QRect(
                    QPoint(indent, indent),
                    QSize(self.size().width() - indent * 2, self.size().height() - indent * 2)
                ), self._round_size_, self._round_size_)

    def paintEvent(self, event: QPaintEvent):
        for state in self.states.active.values():
            for drawer in state.drawers:
                drawer(event)

    def mousePressEvent(self, event: QMouseEvent):
        self._last_mouse_pos_ = event.pos()
        parent = self.parent()
        if parent is None:
            self.activateWindow()

        super(AWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.movable and self._last_mouse_pos_ is not None:
            if self.parent() is None:
                pos = event.globalPos()
                self.move(pos - self._last_mouse_pos_, duration=None)
            else:
                pos = event.globalPos() - self.parent().pos()
                new_pos = pos - self._last_mouse_pos_
                if 0 < new_pos.x() < self.parent().width() - self.width() and 0 < new_pos.y() < self.parent().height() - self.height():
                    self.move(pos - self._last_mouse_pos_, duration=None)
            self._moved_by_mouse_ = True
        else:
            super(AWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._last_mouse_pos_ is not None:
            if self.clickable and not self._moved_by_mouse_:
                self.clicked(self)
            self._last_mouse_pos_ = None
            self._moved_by_mouse_ = False

    @staticmethod
    def getStyleSheet(directory: str):
        file = open(directory, 'r')
        result = file.read()
        file.close()
        return result

    def addTask(self, task, *args, **kwargs):
        from PyAsoka.Processing.AProcess import AProcess
        AProcess.add_task(AProcess.Type.GUI, task, *args, **kwargs)

    def test_animation(self):
        for i in range(3):
            duration = 800 - 200 * (i + 1)
            anim1 = Animation(self, b"geometry")
            anim1.setEndValue(QRect(200, 200, 400, 400))
            anim1.setDuration(duration)
            self._animations_geometry_.add(anim1)

            anim2 = Animation(self, b"geometry")
            anim2.setEndValue(QRect(200, 800, 400, 400))
            anim2.setDuration(duration)
            self._animations_geometry_.add(anim2)

            anim3 = Animation(self, b"geometry")
            anim3.setEndValue(QRect(1200, 800, 400, 400))
            anim3.setDuration(duration)
            self._animations_geometry_.add(anim3)

            anim4 = Animation(self, b"geometry")
            anim4.setEndValue(QRect(600, 400, 400, 400))
            anim4.setDuration(duration)
            self._animations_geometry_.add(anim4)

            anim5 = Animation(self, b"geometry")
            anim5.setEndValue(QRect(200, 200, 1200, 800))
            anim5.setDuration(duration)
            self._animations_geometry_.add(anim5)

            anim6 = Animation(self, b"geometry")
            anim6.setEndValue(QRect(200, 200, 400, 400))
            anim6.setDuration(duration)
            self._animations_geometry_.add(anim6)
        self._animations_geometry_.start()

    def __get_opacity__(self):
        return self._opacity_

    def __set_opacity__(self, opacity):
        self._opacity_ = opacity

        col = self.colors
        stl = self.style
        colors = [col.background, col.background_line, col.frame, col.line, col.text]
        styles = [stl.background, stl.background_line, stl.frame, stl.line, stl.text]
        for i in range(len(colors)):
            if colors[i] is not None:
                colors[i].setAlpha(int(styles[i].alpha() * opacity))

        for child in self.children():
            if issubclass(type(child), AWidget):
                child.__set_opacity__(opacity)

        self.repaint()

    def deleteLater(self):
        self.destroyed(self)
        super(AWidget, self).deleteLater()

    @staticmethod
    def proportional(value, percentage):
        return int(value * percentage / 100)

    alpha = Property(float, __get_opacity__, __set_opacity__)
