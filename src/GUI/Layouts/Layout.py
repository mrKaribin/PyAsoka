from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.GUI.Widget.Widget import Widget, QRect, QPoint, QSize
from PyAsoka.src.Debug.Exceptions import Exceptions
from PyAsoka.Asoka import Asoka


class Size:
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height

    def toQSize(self):
        return QSize(self.width, self.height)


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def toQPoint(self):
        return QPoint(self.x, self.y)


class Layout(Object):
    formalPositionChanged = Signal(QRect)
    formalSizeChanged = Signal(QRect)

    class Spacing:
        def __init__(self, x: int = 1, y: int = 1):
            if isinstance(x, int) and isinstance(y, int):
                self._x_ = x
                self._y_ = y
            else:
                raise Exceptions.UnsupportableType(x, y)

        @property
        def x(self):
            return self._x_

        @property
        def y(self):
            return self._y_

    def __init__(self, parent):
        super().__init__()
        if isinstance(parent, Widget):
            base_widget = parent
        elif isinstance(parent, Layout):
            base_widget = parent.baseWidget
        else:
            raise Exceptions.UnsupportableType(parent)

        self.setParent(parent)
        self._base_widget_ = base_widget
        self._formal_geometry_ = QRect()
        self._items_ = []
        self._layouts_ = []
        self._margin_ = 10
        self._spacing_ = 10
        self._alignment_ = Asoka.Alignment.AlignLeft
        self._stretch_ = Widget.Stretch(False, False)
        self._constrict_ = Widget.Constrict(False, False)
        self._content_size_ = QSize()
        self._minimum_size_ = None
        self._maximum_size_ = None
        self._minimum_content_size_ = QSize()
        self._maximum_content_size_ = QSize()

        self.parent().formalSizeChanged.connect(self.__widget_size_changed__)

    @property
    def widget(self):
        if isinstance(self.parent(), Widget):
            return self.parent()
        else:
            return None

    @widget.setter
    def widget(self, wgt: Widget):
        if isinstance(wgt, Widget):
            self.setParent(wgt)
        else:
            raise Exceptions.UnsupportableType(wgt)

    @property
    def baseWidget(self):
        return self._base_widget_

    @baseWidget.setter
    def baseWidget(self, wgt):
        if isinstance(wgt, Widget):
            self._base_widget_ = wgt
        else:
            raise Exceptions.UnsupportableType(wgt)

    @property
    def items(self):
        return self._items_

    @property
    def layouts(self):
        return self._layouts_

    @property
    def margin(self):
        return self._margin_

    @margin.setter
    def margin(self, value: int):
        if isinstance(value, (int, float)):
            self._margin_ = int(value)
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def spacing(self):
        return self._spacing_

    @spacing.setter
    def spacing(self, value: int):
        if isinstance(value, (int, float)):
            self._spacing_ = int(value)
        else:
            raise Exceptions.UnsupportableType(value)

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
    def constrict(self):
        if self.widget is None:
            return self._constrict_
        else:
            return self.widget.constrict

    @property
    def stretch(self):
        if self.widget is None:
            return self._stretch_
        else:
            return self.widget.stretch

    @property
    def minSize(self):
        if self._minimum_size_ is None:
            return self._minimum_content_size_
        else:
            return self._minimum_size_

    @minSize.setter
    def minSize(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._minimum_size_ = QSize(*value)
        elif isinstance(value, QSize):
            self._minimum_size_ = value
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def maxSize(self):
        if self._maximum_size_ is None:
            return self._maximum_content_size_
        else:
            return self._maximum_size_

    @maxSize.setter
    def maxSize(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._maximum_size_ = QSize(*value)
        elif isinstance(value, QSize):
            self._maximum_size_ = value
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def contentSize(self):
        return self._content_size_

    @contentSize.setter
    def contentSize(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._content_size_ = QSize(*value)
        elif isinstance(value, QSize):
            self._content_size_ = value
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def minContentSize(self):
        return self._minimum_content_size_

    @minContentSize.setter
    def minContentSize(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._minimum_content_size_ = QSize(*value)
        elif isinstance(value, QSize):
            self._minimum_content_size_ = value
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def maxContentSize(self):
        return self._maximum_content_size_

    @maxContentSize.setter
    def maxContentSize(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._maximum_content_size_ = QSize(*value)
        elif isinstance(value, QSize):
            self._maximum_content_size_ = value
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
            self.formalGeometry = value
        else:
            raise Exceptions.UnsupportableType(value)
        # self.formalPositionChanged.emit(self.formalGeometry.topLeft())

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
        # self.formalSizeChanged.emit(self.formalGeometry.size())

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
        # self.formalSizeChanged.emit(self._formal_geometry_.size())
        # self.formalPositionChanged.emit(self._formal_geometry_.topLeft())

    @property
    def availableSize(self):
        if self.widget is not None:
            return self.widget.formalSize
        else:
            return self.formalSize

    def addWidget(self, widget: Widget):
        if isinstance(widget, Widget):
            self.items.append(widget)
            widget.parent = self.baseWidget
            widget.formalSizeChanged.connect(self.__item_size_changed__)
        else:
            raise Exceptions.UnsupportableType(widget)

    def removeWidget(self, widget: Widget):
        if isinstance(widget, Widget):
            self.items.remove(widget)
            widget.disappearance(duration=300)
            self.update()
        else:
            raise Exceptions.UnsupportableType(widget)

    def addLayout(self, layout):
        if isinstance(layout, Layout):
            self.items.append(layout)
            self.layouts.append(layout)
            layout.setParent(self)
            layout.formalSizeChanged.connect(self.__item_size_changed__)
            layout.margin = 0
        else:
            raise Exceptions.UnsupportableType(layout)

    def addSpacing(self, x: int = 1, y: int = 1):
        self.items.append(Layout.Spacing(x, y))

    def __widget_size_changed__(self):
        self.update()

    def __item_size_changed__(self):
        self.update()

    def update(self):
        self.updateItems()

    def init(self):
        for layout in self.layouts:
            layout.init()

        rects = self.getRects()
        if self.widget is None:
            rects = self.adaptRects(rects)

        for item, rect in rects.items():
            item.geometry = rect

    def updateItems(self):
        rects = self.getRects()
        if self.widget is None:
            rects = self.adaptRects(rects)

        for item, rect in rects.items():
            if isinstance(item, Widget):
                item.animate.geometry(rect, duration=300, silent=True)
            elif isinstance(item, Layout):
                item.formalGeometry = rect
                item.update()

    def updateSizes(self):
        pass

    def adaptRects(self, rects: dict):
        globalPos = QPoint(0, 0)
        current = self
        while True:
            if current.widget is None:
                globalPos += current.formalPosition
                current = current.parent()
            else:
                break

        if globalPos.x() != 0 or globalPos.y() != 0:
            for item, rect in rects.items():
                rects[item] = QRect(rect.topLeft() + globalPos, rect.size())
        return rects

    def getRects(self) -> dict:
        pass
