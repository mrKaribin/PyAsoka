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
from PyAsoka.Asoka import Asoka

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
    formalPositionChanged = Signal(QRect)
    formalSizeChanged = Signal(QRect)
    destroyed = Signal(QWidget)
    _run_gui_task_ = Signal(types.MethodType, list)

    class Stretch:
        def __init__(self, x, y):
            if isinstance(x, (bool, int)) and isinstance(y, (bool, int)):
                self._x_ = x
                self._y_ = y
            else:
                raise Exceptions.UnsupportableType(x, y)

        @property
        def x(self):
            return self._x_

        @x.setter
        def x(self, value):
            if isinstance(value, (bool, int)):
                self._x_ = value
            else:
                raise Exceptions.UnsupportableType(value)

        @property
        def y(self):
            return self._y_

        @y.setter
        def y(self, value):
            if isinstance(value, (bool, int)):
                self._y_ = value
            else:
                raise Exceptions.UnsupportableType(value)

    class Constrict:
        def __init__(self, x, y):
            if isinstance(x, bool) and isinstance(y, bool):
                self._x_ = x
                self._y_ = y
            else:
                raise Exceptions.UnsupportableType(x, y)

        @property
        def x(self):
            return self._x_

        @x.setter
        def x(self, value):
            if isinstance(value, bool):
                self._x_ = value
            else:
                raise Exceptions.UnsupportableType(value)

        @property
        def y(self):
            return self._y_

        @y.setter
        def y(self, value):
            if isinstance(value, bool):
                self._y_ = value
            else:
                raise Exceptions.UnsupportableType(value)

    class AspectRatio:
        def __init__(self, x=None, y=None):
            if isinstance(x, bool) and isinstance(y, bool):
                self._x_ = x
                self._y_ = y
                self._state_ = True
            else:
                self._x_ = None
                self._y_ = None
                self._state_ = False

        def __bool__(self):
            return self._state_

        @property
        def x(self):
            return self._x_

        @property
        def y(self):
            return self._y_

    def __init__(self, parent: QWidget = None, movable: bool = False, clickable: bool = False, keyboard: bool = False,
                 style: type(Style) = None,
                 size: tuple | QSize = None, position: tuple | QPoint = None, geometry: tuple | QRect = None,
                 min_size: tuple | QSize = None, max_size: tuple | None = None,
                 alignment: Asoka.Alignment = Asoka.Alignment.AlignLeft, stretch: tuple = (False, False),
                 constrict: tuple = (False, False), aspect_ratio: tuple | None = False):
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
        # managers
        self._layers_ = createManager('layers', LayerManager)
        self._states_ = createManager('states', StateManager)
        self._mouse_ = MouseManager(self)
        self._props_ = self._props_class_(self)
        self._animations_ = AnimationManager()
        self._animate_ = Animate(self)
        self._style_ = StyleManager(self, style)
        # visualization
        self._formal_geometry_ = QRect()
        self._alignment_ = Asoka.Alignment.AlignLeft
        self._stretch_ = Widget.Stretch(False, False)
        self._constrict_ = Widget.Constrict(False, False)
        self._aspect_ratio_ = Widget.AspectRatio()
        self._layout_ = None
        # behavior
        self._movable_ = movable
        self._clickable_ = clickable

        self._loading_movie_ = QMovie('PyAsoka/media/gif/loading_background2.gif')
        self._loading_movie_.frameChanged.connect(self.repaint)

        # class preparation
        self.parent = parent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        if self.parent is None:
            self.setWindowFlag(Qt.WindowType.Tool)
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            # self.setWindowFlag(Qt.WindowType.ToolTip)
            # self.setWindowFlag(Qt.WindowType.BypassWindowManagerHint)
            # self.setWindowFlag(Qt.WindowType.WindowOverridesSystemGestures)

        if keyboard:
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        if size is not None:
            self.size = size
        if position is not None:
            self.position = position
        if geometry is not None:
            self.geometry = geometry
        if min_size is not None:
            self.minSize = min_size
        if max_size is not None:
            self.maxSize = max_size
        if isinstance(stretch, tuple) and len(stretch) == 2:
            self.stretch.x = stretch[0]
            self.stretch.y = stretch[1]
        if isinstance(constrict, tuple) and len(constrict) == 2:
            self.constrict.x = constrict[0]
            self.constrict.y = constrict[1]
        self.alignment = alignment
        self.aspectRatio = aspect_ratio

        # Подготовка соединений с сигналами
        def run_gui_task(method, args):
            method(*args)

        self._run_gui_task_.connect(run_gui_task)

        # Запуск виджета
        def __preparation__():
            self.prepare()
            self.runGuiTask(self.states.loading.disable)

        self.layers.background.enable(duration=None)
        if self.__class__.prepare != Widget.prepare:
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

    # Properties -------------------------------------------------------------------------------------------------------

    @Property(float)
    def alpha(self):
        return self.props.alpha

    @property
    def parent(self):
        return QWidget.parent(self)

    @parent.setter
    def parent(self, parent):
        if isinstance(parent, Widget):
            self.setParent(parent)
            parent.props._alpha_.changed.connect(lambda value: self.props._alpha_.__setter__(self, value))
        elif parent is None:
            self.setParent(parent)
        else:
            raise Exceptions.UnsupportableType(parent)

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
    def size(self):
        return QWidget.size(self)

    @size.setter
    def size(self, size):
        if isinstance(size, tuple) and len(size) == 2:
            self.resize(QSize(*size))
        elif isinstance(size, QSize):
            self.resize(size)
        else:
            raise Exceptions.UnsupportableType(size)
        self.formalSize = QWidget.size(self)

    @property
    def position(self):
        return self.pos()

    @position.setter
    def position(self, position):
        if isinstance(position, tuple) and len(position) == 2:
            self.move(QPoint(*position))
        elif isinstance(position, QPoint):
            self.move(position)
        else:
            raise Exceptions.UnsupportableType(position)
        self.formalPosition = self.pos()

    @property
    def geometry(self):
        return QWidget.geometry(self)

    @geometry.setter
    def geometry(self, geometry):
        if isinstance(geometry, tuple) and len(geometry) == 4:
            super(Widget, self).setGeometry(QRect(*geometry))
        elif isinstance(geometry, QRect):
            super(Widget, self).setGeometry(geometry)
        else:
            raise Exceptions.UnsupportableType(geometry)
        self.formalGeometry = QWidget.geometry(self)

    @property
    def minSize(self):
        return self.minimumSize()

    @minSize.setter
    def minSize(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self.setMinimumSize(QSize(*value))
        elif isinstance(value, QSize):
            self.setMinimumSize(value)
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def maxSize(self):
        return self.maximumSize()

    @maxSize.setter
    def maxSize(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self.setMaximumSize(QSize(*value))
        elif isinstance(value, QSize):
            self.setMaximumSize(value)
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def formalPosition(self):
        return self.formalGeometry.topLeft()

    @formalPosition.setter
    def formalPosition(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self.formalGeometry = QRect(QPoint(*value), self.formalGeometry.size())
        elif isinstance(value, QPoint):
            self.formalGeometry = QRect(value, self.formalGeometry.size())
        else:
            raise Exceptions.UnsupportableType(value)
        self.formalPositionChanged.emit(self.formalGeometry.topLeft())

    @property
    def formalSize(self):
        return self.formalGeometry.size()

    @formalSize.setter
    def formalSize(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self.formalGeometry = QRect(self.formalGeometry.topLeft(), QSize(*value))
        elif isinstance(value, QSize):
            self.formalGeometry = QRect(self.formalGeometry.topLeft(), value)
        else:
            raise Exceptions.UnsupportableType(value)
        self.formalSizeChanged.emit(self.formalGeometry.size())

    @property
    def formalGeometry(self):
        return self._formal_geometry_

    @formalGeometry.setter
    def formalGeometry(self, value):
        if isinstance(value, QRect):
            self._formal_geometry_ = value
        elif isinstance(value, tuple) and len(value) == 4:
            self._formal_geometry_ = QRect(*value)
        else:
            raise Exceptions.UnsupportableType(value)
        self.formalSizeChanged.emit(self._formal_geometry_.size())
        self.formalPositionChanged.emit(self._formal_geometry_.topLeft())

    @property
    def alignment(self):
        return self._alignment_

    @alignment.setter
    def alignment(self, value: Asoka.Alignment):
        if isinstance(value, Asoka.Alignment):
            self._alignment_ = value
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def stretch(self):
        return self._stretch_

    @property
    def constrict(self):
        return self._constrict_

    @property
    def aspectRatio(self):
        return self._aspect_ratio_

    @aspectRatio.setter
    def aspectRatio(self, value):
        if value is False:
            self._aspect_ratio_ = Widget.AspectRatio()
        elif isinstance(value, tuple) and len(value) == 2:
            self._aspect_ratio_ = Widget.AspectRatio(*value)
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def layout(self):
        return self._layout_

    @layout.setter
    def layout(self, layout):
        from PyAsoka.src.GUI.Layouts.Layout import Layout
        if isinstance(layout, Layout):
            self._layout_ = layout
        else:
            raise Exceptions.UnsupportableType(layout)


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

    def prepare(self):
        pass

    # Methods ----------------------------------------------------------------------------------------------------------

    def __get_painter__(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        parent = self.parent
        if parent is None:
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_DestinationOver)
        elif issubclass(type(parent), Widget) and (
                not parent.style.current.exists('background') or parent.style.current.background.alpha() != 255):
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)
        else:
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceIn)
        return painter

    def appearance(self, duration=1000):
        self.alpha = 0.0
        self.show()
        anim = self.animate.opacity(1.0, 0.0, duration)
        return anim

    def disappearance(self, duration=1000, with_delete=False):
        anim = self.animate.opacity(0.0, duration=duration)
        anim.finished.connect(self.hide)
        if with_delete is True:
            anim.finished.connect(self.deleteLater)
        return anim

    def runGuiTask(self, method, args=[]):
        self._run_gui_task_.emit(method, args)

    def deleteLater(self):
        self.destroyed.emit(self)
        super(Widget, self).deleteLater()

    # Events ----------------------------------------------------------------------------------------------------------

    def enterEvent(self, event):
        pass

    def leaveEvent(self, event):
        self.mouse.cursorPosition = None

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resized.emit(self.geometry)

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

    @staticmethod
    def proportional(value, percentage):
        return int(value * percentage / 100)
