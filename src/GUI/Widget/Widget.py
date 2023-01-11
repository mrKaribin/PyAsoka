from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from PySide6.QtGui import QPaintEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Property, QPoint, QRect, QSize
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.GUI.Style.Styles import Styles, Style, Color
from PyAsoka.src.GUI.API.Screen import Screen
from PyAsoka.src.GUI.AnimationManager import AnimationManager, Animation
from PyAsoka.src.GUI.Widget.Layer import Layer
from PyAsoka.src.GUI.Widget.LayerManager import LayerManager
from PyAsoka.src.GUI.Widget.MouseManager import MouseManager
from PyAsoka.src.GUI.Widget.Configuration import Configuration
from PyAsoka.src.GUI.Widget.StyleManager import StyleManager

from threading import Timer


class Widget(QWidget):

    def __init__(self, parent: QWidget = None, movable: bool = False, clickable: bool = False, keyboard: bool = False,
                 geometry: tuple = None, style: Style = None, animated: bool = True,
                 frame_size: int = 2, round_size: int = 20,
                 with_super: bool = True):
        if with_super:
            super().__init__(parent)

        if parent is not None:
            pass

        # public
        self.movable = movable
        self.clickable = clickable
        self.animated = animated

        # private
        self._layers_ = LayerManager()\
            .add(Layer('loading',           self.renderLoader)) \
            .add(Layer('background',        self.renderBackground))
        self._style_ = StyleManager(self, style)
        self._mouse_ = MouseManager()
        self._configuration_ = Configuration(self, 1.0)

        self._opacity_ = 1.0
        self._default_opacity_ = 1.0
        self._frame_size_ = frame_size
        self._round_size_ = round_size
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
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        if geometry is not None:
            if isinstance(geometry, tuple) or isinstance(geometry, list):
                self.setGeometry(QRect(*geometry), duration=None)
            if isinstance(geometry, QRect):
                self.setGeometry(geometry, duration=None)

        self.layers.loading.enable()
        self._initialization_timer_.start()

    def __preparation__(self):
        self.preparation()
        self.layers.loading.disable()
        self.layers.background.enable()

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
        style = self.style.default
        if self.animated and self.parent() is None and style.background is not None and style.background.alpha() < 255:
            color = Color(self.style.current.background)
            color.setAlpha(255)
            self.setColor(self.style.current.background, color, 200, Animation.Type.PARALLEL)

    def leaveEvent(self, event):
        style = self.style.default
        if self.animated and self.parent() is None and style.background is not None and style.background.alpha() < 255:
            self.setColor(self.style.current.background, style.background, 200, Animation.Type.PARALLEL)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resized(self.geometry())

    def __get_painter__(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        parent = self.parent()
        if parent is None:
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_DestinationOver)
        elif issubclass(type(parent), Widget) and (
                parent.style.current.background is None or parent.style.current.background.alpha() != 255):
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)
        else:
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceIn)
        return painter

    def renderLoader(self, event: QPaintEvent):
        pass

    def renderBackground(self, event: QPaintEvent):
        if self.style.current.frame is not None or self.style.current.background is not None:
            painter = self.__get_painter__()
            pen_size = self._frame_size_
            if self.style.current.frame is not None:
                painter.setPen(QPen(self.style.current.frame, pen_size))
            else:
                painter.setPen(QPen(self.style.current.background, pen_size))
            if self.style.current.background is not None:
                painter.setBrush(QBrush(self.style.current.background))
            indent = int(pen_size * 1.5)
            painter.drawRoundedRect(QRect(
                QPoint(indent, indent),
                QSize(self.size().width() - indent * 2, self.size().height() - indent * 2)
            ), self._round_size_, self._round_size_)

    def paintEvent(self, event: QPaintEvent):
        self.layers.paint(self)

    def mousePressEvent(self, event: QMouseEvent):
        parent = self.parent()
        if parent is None:
            self.activateWindow()

        self.mouse.pressEvent(event)
        super(Widget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.movable and self.mouse.leftButton.pressed:
            lastPos = self.mouse.leftButton.pressPosition

            if self.parent() is None:
                pos = event.globalPos()
                self.move(pos - lastPos, duration=None)

            else:
                pos = event.globalPos() - self.parent().pos()
                new_pos = pos - lastPos
                if 0 < new_pos.x() < self.parent().width() - self.width() and 0 < new_pos.y() < self.parent().height() - self.height():
                    self.move(pos - lastPos, duration=None)
            self._moved_by_mouse_ = True

        else:
            super(Widget, self).mouseMoveEvent(event)
        self.mouse.moveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.clickable and not self._moved_by_mouse_:
            self.clicked(self)
        self._moved_by_mouse_ = False

        self.mouse.releaseEvent(event)
        super(Widget, self).mouseReleaseEvent(event)

    @staticmethod
    def getStyleSheet(directory: str):
        file = open(directory, 'r')
        result = file.read()
        file.close()
        return result

    def addTask(self, task, *args, **kwargs):
        pass

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

    def deleteLater(self):
        self.destroyed(self)
        super(Widget, self).deleteLater()

    def __get_opacity__(self):
        self.conf.display.__get_opacity__()

    def __set_opacity__(self, opacity):
        self.conf.display.__set_opacity__(opacity)

    alpha = Property(float, __get_opacity__, __set_opacity__)

    @property
    def layers(self):
        return self._layers_

    @property
    def style(self) -> StyleManager:
        return self._style_

    @property
    def mouse(self):
        return self._mouse_

    @property
    def conf(self):
        return self._configuration_

    @staticmethod
    def proportional(value, percentage):
        return int(value * percentage / 100)
