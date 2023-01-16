from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath
from PySide6.QtGui import QPaintEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Property, QPoint, QRect, QSize

from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.GUI.Style.Styles import Style, Color
from PyAsoka.src.GUI.API.Screen import Screen
from PyAsoka.src.GUI.Widget.AnimationManager import AnimationManager, Animation
from PyAsoka.src.GUI.Widget.Configuration import Configuration
from PyAsoka.src.GUI.Widget.MouseManager import MouseManager
from PyAsoka.src.GUI.Widget.StyleManager import StyleManager
from PyAsoka.src.GUI.Widget.Prop import Prop
from PyAsoka.src.GUI.Widget.Props import Props, PropsMeta
from PyAsoka.src.GUI.Widget.Layer import Layer
from PyAsoka.src.GUI.Widget.LayerManager import LayerManager
from PyAsoka.src.GUI.Widget.State import State
from PyAsoka.src.GUI.Widget.StateManager import StateManager

from threading import Timer
from copy import copy

import inspect
import types


class WidgetMeta(type(QWidget)):
    def __new__(mcs, name, bases, attrs, **extra_kwargs):
        def createManager(mng_name, manager_type, element_type):
            bases_list = {}
            for base in bases:
                if f'_{mng_name}_' in base.__dict__.keys():
                    bases_list = {**bases_list, **base.__dict__[f'_{mng_name}_list_']}

            manager = manager_type()
            if f'_{mng_name}_list_' not in attrs:
                attrs[f'_{mng_name}_list_'] = {}
            attrs[f'_{mng_name}_list_'] = {**attrs[f'_{mng_name}_list_'], **bases_list}

            for key in list(attrs.keys()):
                attr = attrs[key]
                if isinstance(attr, type) and issubclass(attr, element_type):
                    attrs.pop(key)
                    lay_name = key[0].lower() + key[1:]
                    attrs[f'_{mng_name}_list_'][lay_name] = attr

            if f'_{mng_name}_list_' in attrs:
                for key, layer in attrs[f'_{mng_name}_list_'].items():
                    manager.add(key, layer())

            attrs[f'_{mng_name}_'] = manager

        createManager('layers', LayerManager, Layer)
        createManager('states', StateManager, State)
        attrs[f'_mouse_'] = MouseManager()

        # Поиск Props
        props_list = {}
        for base in bases:
            if f'_props_' in base.__dict__.keys():
                props_list = {**props_list, **base.__dict__[f'_props_list_']}

        if f'_props_list_' not in attrs:
            attrs[f'_props_list_'] = {}
        props_list = {**attrs[f'_props_list_'], **props_list}

        for key in list(attrs.keys()):
            attr = attrs[key]
            cond = isinstance(attr, type) and (issubclass(attr, Prop) or issubclass(attr, Props))
            if isinstance(attr, Prop) or cond:
                attrs.pop(key)
                lay_name = key[0].lower() + key[1:]
                if isinstance(attr, Prop):
                    props_list[lay_name] = attr
                else:
                    props_list[lay_name] = attr

        props = PropsMeta('WidgetProps', (Props, ), props_list)()
        attrs[f'_props_'] = props
        attrs[f'_props_list_'] = props_list

        return super().__new__(mcs, name, bases, attrs)


class Widget(QWidget, metaclass=WidgetMeta):

    clicked = Signal(QWidget)
    resized = Signal(QRect)
    destroyed = Signal(QWidget)
    _run_gui_task_ = Signal(types.MethodType, list)

    def __init__(self, parent: QWidget = None, movable: bool = False, clickable: bool = False, keyboard: bool = False,
                 geometry: tuple = None, style: Style = None, animated: bool = True,
                 with_super: bool = True):
        if with_super:
            super().__init__(parent)

        if parent is not None:
            pass

        # public
        self.animated = animated

        # private
        self.layers.setWidget(self)
        self.states.setWidget(self)
        self.mouse.setWidget(self)
        self.props.setWidget(self)
        self._style_ = StyleManager(self, style)
        self._configuration_ = Configuration(self, movable, clickable)

        self._moved_by_mouse_ = False

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

        if False:
            if geometry is not None:
                if isinstance(geometry, tuple) or isinstance(geometry, list):
                    self.setGeometry(QRect(*geometry), duration=None)
                if isinstance(geometry, QRect):
                    self.setGeometry(geometry, duration=None)

        # Подготовка соединений с сигналами
        def run_gui_task(method, args):
            method(*args)

        self._run_gui_task_.connect(run_gui_task)

        def __preparation__():
            self.prepare()
            self.runGuiTask(self.states.loading.disable)

        self.layers.background.enable()
        self.states.loading.enable()
        self._initialization_timer_ = Timer(0.05, __preparation__)
        self._initialization_timer_.start()

    # Properties -------------------------------------------------------------------------------------------------------
    class Alpha(Prop, type=float, default=1.0):
        def setter(self, widget, value):
            self.value = value

            col = widget.style.current
            stl = widget.style.default
            current = [col.background, col.background_line, col.frame, col.line, col.text]
            default = [stl.background, stl.background_line, stl.frame, stl.line, stl.text]

            for i in range(len(current)):
                if current[i] is not None:
                    current[i].setAlpha(int(default[i].alpha() * value))

            for child in widget.children():
                if issubclass(type(child), Widget):
                    child.props.alpha = value

    class Frame(Props):
        thickness = Prop(int, 2)
        anglesRadius = Prop(int, 20)
        topLeft = Prop(int, True)
        topRight = Prop(int, True)
        bottomLeft = Prop(int, True)
        bottomRight = Prop(int, True)

        def setRoundedAngles(self, top_left: bool, top_right: bool, bottom_left: bool, bottom_right: bool):
            self.topLeft = top_left
            self.topRight = top_right
            self.bottomLeft = bottom_left
            self.bottomRight = bottom_right

    # Layers -----------------------------------------------------------------------------------------------------------
    class Background(Layer, level=Layer.Level.TOP):
        def paint(self, widget, painter, event):
            if widget.style.current.frame is not None or widget.style.current.background is not None:
                painter = widget.__get_painter__()
                thickness = widget.props.frame.thickness
                angle_size = widget.props.frame.anglesRadius
                angle_side = angle_size * 2
                indent = int(thickness * 1.5)

                # Готовим перо для отрисовки рамки
                if widget.style.current.frame is not None:
                    frame = widget.style.current.frame
                    painter.setPen(QPen(frame, thickness))
                else:
                    background = widget.style.current.background
                    painter.setPen(QPen(background, thickness))

                # Готовим заливку для фона
                if widget.style.current.background is not None:
                    painter.setBrush(QBrush(widget.style.current.background))

                # print(self.style.default.background.alpha())
                path = QPainterPath()
                path.moveTo(0, angle_size)
                if widget.props.frame.topLeft:
                    path.arcTo(QRect(0, 0, angle_side, angle_side), 180, -90)
                else:
                    path.lineTo(0, 0)
                    path.lineTo(angle_size, 0)

                path.lineTo(widget.width() - angle_size, 0)
                if widget.props.frame.topRight:
                    path.arcTo(QRect(widget.width() - angle_side, 0, angle_side, angle_side), 90, -90)
                else:
                    path.lineTo(widget.width(), 0)
                    path.lineTo(widget.width(), angle_size)

                path.lineTo(widget.width(), widget.height() - angle_size)
                if widget.props.frame.bottomRight:
                    path.arcTo(QRect(widget.width() - angle_side, widget.height() - angle_side, angle_side, angle_side),
                               0, -90)
                else:
                    path.lineTo(widget.width(), widget.height())
                    path.lineTo(widget.width() - angle_side, widget.height())

                path.lineTo(angle_size, widget.height())
                if widget.props.frame.bottomLeft:
                    path.arcTo(QRect(0, widget.height() - angle_side, angle_side, angle_side), 270, -90)
                else:
                    path.lineTo(0, widget.height())
                    path.lineTo(0, widget.height() - angle_size)

                path.lineTo(0, angle_size)
                painter.drawPath(path)

    # States -----------------------------------------------------------------------------------------------------------
    class Loading(State):
        def animation(self, widget):
            from PyAsoka.src.GUI.Animation.CycleAnimations import CycleAnimations
            return CycleAnimations(
                Animation(widget.props, b'alpha', 1.0, 0.5, 500),
                Animation(widget.props, b'alpha', 0.5, 1.0, 500)
            )

        def endAnimation(self, widget):
            from PyAsoka.src.GUI.Animation.Animation import Animation
            return Animation(widget, b'alpha', widget.alpha, 1.0, 500)

    # Methods ----------------------------------------------------------------------------------------------------------
    def prepare(self):
        from time import sleep
        sleep(4.7)
        # print('Loading finished')

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
        self.resized.emit(self.geometry())

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

    def paintEvent(self, event: QPaintEvent):
        self.layers.paint(self.__get_painter__(), event)

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse.pressEvent(event)
        super(Widget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        super(Widget, self).mouseMoveEvent(event)
        self.mouse.moveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse.releaseEvent(event)
        super(Widget, self).mouseReleaseEvent(event)

    def runGuiTask(self, method: types.MethodType, args=[]):
        self._run_gui_task_.emit(method, args)

    def deleteLater(self):
        self.destroyed.emit(self)
        super(Widget, self).deleteLater()

    @Property(float)
    def alpha(self):
        return self.props.alpha

    @alpha.getter
    def alpha(self):
        return self.props.alpha

    @alpha.setter
    def alpha(self, opacity):
        self.props.alpha = opacity

    @property
    def layers(self) -> LayerManager:
        return self._layers_

    @property
    def states(self) -> StateManager:
        return self._states_

    @property
    def style(self) -> StyleManager:
        return self._style_

    @property
    def mouse(self):
        return self._mouse_

    @property
    def conf(self):
        return self._configuration_

    @property
    def props(self):
        return self._props_

    @staticmethod
    def proportional(value, percentage):
        return int(value * percentage / 100)
