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
from PyAsoka.src.GUI.Widget.Animate import Animate
from PyAsoka.src.GUI.Style.Styles import Styles, Style, Color
from PyAsoka.src.GUI.API.Screen import Screen
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.src.Debug.Exceptions import Exceptions

from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath
from PySide6.QtGui import QPaintEvent, QMouseEvent, QResizeEvent, QMovie, QPixmap, QImage
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Property, QPoint, QRect, QSize

from threading import Timer
from copy import copy

import inspect
import types


class WidgetMeta(type(QWidget)):
    def __new__(mcs, name, bases, attrs, **extra_kwargs):
        def createManager(mng_name, manager_type, element_type):
            list_name = f'_{mng_name}_list_'
            bases_list = {}
            for base in bases:
                if list_name in base.__dict__.keys():
                    bases_list = {**bases_list, **base.__dict__[list_name]}

            for key in list(attrs.keys()):
                attr = attrs[key]
                if isinstance(attr, type) and issubclass(attr, element_type):
                    attrs.pop(key)
                    lay_name = key[0].lower() + key[1:]
                    bases_list[lay_name] = attr
            attrs[list_name] = bases_list

        def createProps():
            props_base = Props
            for base in bases:
                if f'_props_class_' in base.__dict__.keys():
                    props_base = base.__dict__[f'_props_class_']

            props_attrs = {}
            if 'Props' in attrs.keys():
                props = attrs['Props'].__dict__
                for key in list(props.keys()):
                    attr = props[key]
                    if isinstance(attr, Prop) or isinstance(attr, type):
                        lay_name = key[0].lower() + key[1:]
                        props_attrs[lay_name] = attr
                attrs.pop('Props')

            attrs[f'_props_class_'] = PropsMeta('WidgetProps', (props_base, ), props_attrs)

        createManager('layers', LayerManager, Layer)
        createManager('states', StateManager, State)
        createProps()

        # Поиск Props

        return super().__new__(mcs, name, bases, attrs)


class Widget(QWidget, metaclass=WidgetMeta):

    clicked = Signal(QWidget)
    resized = Signal(QRect)
    destroyed = Signal(QWidget)
    _run_gui_task_ = Signal(types.MethodType, list)

    def __init__(self, parent: QWidget = None, movable: bool = False, clickable: bool = False, keyboard: bool = False,
                 style: type(Style) = None,
                 size: tuple | QSize = None, position: tuple | QPoint = None, geometry: tuple | QRect = None,
                 with_super: bool = True):
        if with_super:
            super().__init__(parent)

        if style is None:
            style = Styles.Window if parent is None else Styles.Widget

        def createManager(mng_name, manager_type):
            list_name = f'_{mng_name}_list_'
            manager = manager_type(self)
            attrs = getattr(self, list_name, None)
            if attrs is not None:
                for key, item in attrs.items():
                    manager.add(key, item(self))
            return manager

        # public
        self.animation = None

        # private
        self._layers_ = createManager('layers', LayerManager)
        self._states_ = createManager('states', StateManager)
        self._mouse_ = MouseManager(self)
        self._props_ = self._props_class_(self)
        self._animations_ = AnimationManager()
        self._animate_ = Animate(self)
        self._style_ = StyleManager(self, style)
        self._movable_ = movable
        self._clickable_ = clickable

        self._loading_movie_ = QMovie('PyAsoka/media/gif/loading_background2.gif')
        self._loading_movie_.frameChanged.connect(self.repaint)

        # class preparation
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        if self.parent() is None:
            self.setWindowFlag(Qt.WindowType.ToolTip)
            # self.setWindowFlag(Qt.WindowType.BypassWindowManagerHint)
            # self.setWindowFlag(Qt.WindowType.WindowOverridesSystemGestures)

        if keyboard:
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        if size is not None:
            self.setSize(size)
        if position is not None:
            self.setPosition(position)
        if geometry is not None:
            self.setGeometry(geometry)

        # Подготовка соединений с сигналами
        def run_gui_task(method, args):
            method(*args)

        self._run_gui_task_.connect(run_gui_task)
        if parent is not None:
            parent.props._alpha_.changed.connect(lambda value: self.props._alpha_.__setter__(self, value))
        # self.props._alpha_.changed.connect(self.repaint)

        # Запуск виджета
        def __preparation__():
            self.prepare()
            self.runGuiTask(self.states.loading.disable)

        self.layers.background.enable(duration=None)
        self.states.loading.enable()
        self._initialization_timer_ = Timer(0.05, __preparation__)
        self._initialization_timer_.start()

    # Properties -------------------------------------------------------------------------------------------------------
    class Props:
        class Alpha(Prop, type=float, default=1.0):
            def setter(self, widget, value):
                self.value = value

        class Frame:
            thickness = Prop(int, 3)
            anglesRadius = Prop(int, 15)
            topLeft = Prop(bool, True)
            topRight = Prop(bool, True)
            bottomLeft = Prop(bool, True)
            bottomRight = Prop(bool, True)

            def setRoundedAngles(self, top_left: bool, top_right: bool, bottom_left: bool, bottom_right: bool):
                self.topLeft = top_left
                self.topRight = top_right
                self.bottomLeft = bottom_left
                self.bottomRight = bottom_right

    # Layers -----------------------------------------------------------------------------------------------------------
    class Background(Layer, level=Layer.Level.BOTTOM):
        def paint(self, widget, painter, style, props, event):
            if style.exists('frame') or style.exists('background'):
                thickness = widget.props.frame.thickness
                angle_size = widget.props.frame.anglesRadius
                angle_side = angle_size * 2
                indent = int(thickness * 0.7)

                # Готовим перо для отрисовки рамки
                if style.exists('frame'):
                    frame = style.frame
                    painter.setPen(QPen(frame, thickness))
                else:
                    background = style.background
                    painter.setPen(QPen(background, thickness))

                # Готовим заливку для фона
                if style.exists('background'):
                    painter.setBrush(QBrush(style.background))

                path = QPainterPath()
                path.moveTo(indent, angle_size + indent)
                if widget.props.frame.topLeft:
                    path.arcTo(QRect(indent, indent, angle_side, angle_side), 180, -90, )
                else:
                    path.lineTo(indent, indent)
                    path.lineTo(angle_size + indent, indent)

                path.lineTo(widget.width() - angle_size - indent, indent)
                if widget.props.frame.topRight:
                    path.arcTo(QRect(widget.width() - angle_side - indent, indent, angle_side, angle_side), 90, -90)
                else:
                    path.lineTo(widget.width() - indent, indent)
                    path.lineTo(widget.width() - indent, angle_size - indent)

                path.lineTo(widget.width() - indent, widget.height() - angle_size - indent)
                if widget.props.frame.bottomRight:
                    path.arcTo(QRect(widget.width() - angle_side - indent, widget.height() - angle_side - indent, angle_side, angle_side), 0, -90)
                else:
                    path.lineTo(widget.width() - indent, widget.height() - indent)
                    path.lineTo(widget.width() - angle_side - indent, widget.height() - indent)

                path.lineTo(angle_size + indent, widget.height() - indent)
                if widget.props.frame.bottomLeft:
                    path.arcTo(QRect(indent, widget.height() - angle_side - indent, angle_side, angle_side), 270, -90)
                else:
                    path.lineTo(indent, widget.height() - indent)
                    path.lineTo(indent, widget.height() - angle_size - indent)

                path.lineTo(indent, angle_size + indent)
                painter.drawPath(path)

    class LoadingBackground(Layer, level=Layer.Level.MIDDLE):
        def paint(self, widget, painter: QPainter, style, props: Props, event: QPaintEvent):
            pixmap = widget._loading_movie_.currentPixmap()
            size = QSize(160 * 3, 120 * 3)
            pos = QPoint((widget.width() - size.width()) // 2, (widget.height() - size.height()) // 2)
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)
            painter.setOpacity(self.alpha)
            painter.drawPixmap(QRect(pos, size), pixmap)
            painter.setOpacity(1.0)

    # States -----------------------------------------------------------------------------------------------------------
    class Loading(State):
        def task(self, widget):
            widget.layers.loadingBackground.enable(duration=300)
            widget._loading_movie_.start()

        def endTask(self, widget):
            anim = widget.layers.loadingBackground.disappearance()
            anim.finished.connect(widget._loading_movie_.stop)

    # Methods ----------------------------------------------------------------------------------------------------------

    def prepare(self):
        pass

    def setSize(self, size):
        if isinstance(size, tuple) and len(size) == 2:
            self.resize(QSize(*size))
        elif isinstance(size, QSize):
            self.resize(size)
        else:
            raise Exceptions.UnsupportableType(size)

    def setPosition(self, position):
        if isinstance(position, tuple) and len(position) == 2:
            self.move(QPoint(*position))
        elif isinstance(position, QPoint):
            self.move(position)
        else:
            raise Exceptions.UnsupportableType(position)

    def setGeometry(self, geometry):
        if isinstance(geometry, tuple) and len(geometry) == 4:
            super(Widget, self).setGeometry(QRect(*geometry))
        elif isinstance(geometry, QRect):
            super(Widget, self).setGeometry(geometry)
        else:
            raise Exceptions.UnsupportableType(geometry)

    def appearance(self, duration=1000):
        self.show()
        self.animate.opacity(1.0, 0.0, duration)

    def disappearance(self, duration=1000, with_delete=False):
        anim = self.animate.opacity(0.0, duration=duration)
        anim.finished.connect(self.hide)
        if with_delete is True:
            anim.finished.connect(self.deleteLater)

    def enterEvent(self, event):
        pass

    def leaveEvent(self, event):
        self.mouse.cursorPosition = None

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resized.emit(self.geometry())

    def __get_painter__(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        parent = self.parent()
        if parent is None:
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_DestinationOver)
        elif issubclass(type(parent), Widget) and (
                not parent.style.current.exists('background') or parent.style.current.background.alpha() != 255):
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
    def movable(self):
        return self._movable_

    @movable.setter
    def movable(self, value):
        if isinstance(value, bool):
            self._movable_ = value
        else:
            Exceptions.UnsupportableType(value)

    @property
    def clickable(self):
        return self._clickable_

    @clickable.setter
    def clickable(self, value):
        if isinstance(value, bool):
            self._clickable_ = value
        else:
            Exceptions.UnsupportableType(value)

    @property
    def props(self):
        return self._props_

    @property
    def animations(self) -> AnimationManager:
        return self._animations_

    @property
    def animate(self) -> Animate:
        return self._animate_

    @property
    def painter(self) -> QPainter:
        return self.__get_painter__()

    @staticmethod
    def proportional(value, percentage):
        return int(value * percentage / 100)
