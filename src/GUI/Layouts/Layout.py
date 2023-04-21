from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.GUI.Widget.Widget import Widget, QRect, QPoint, QSize
from PyAsoka.src.Debug.Exceptions import Exceptions


class Layout(Object):
    formalPositionChanged = Signal(QRect)
    formalSizeChanged = Signal(QRect)

    def __init__(self, parent, base_widget=None):
        super().__init__()
        self.setParent(parent)
        if isinstance(parent, Widget):
            base_widget = parent
        self._base_widget_ = base_widget
        self._formal_geometry_ = QRect()
        self._items_ = []
        self._layouts_ = []
        self._margin_ = 10
        self._spacing_ = 10
        self._size_ = QSize()
        self._minimum_size_ = QSize()
        self._maximum_size_ = QSize()

        self.widget.formalSizeChanged.connect(self.__widget_size_changed__)

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
    def size(self):
        return self._size_

    @size.setter
    def size(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._size_ = QSize(*value)
        elif isinstance(value, QSize):
            self._size_ = value
        else:
            raise Exceptions.UnsupportableType(value)

    @property
    def minSize(self):
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
    def formalPosition(self):
        return self._formal_geometry_

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
            widget.setParent(self.widget)
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
            if self.baseWidget is not None:
                layout.baseWidget = self.baseWidget
            else:
                raise Exception('Базовый виджет не определен для этого компоновщика')
            layout.setParent(self.baseWidget)
            layout.formalSizeChanged.connect(self.__item_size_changed__)
        else:
            raise Exceptions.UnsupportableType(layout)

    def __widget_size_changed__(self):
        self.update()

    def __item_size_changed__(self):
        self.update()

    def update(self):
        self.updateItems()

    def init(self):
        rects = self.getRects()
        for item, rect in rects.items():
            item.geometry = rect

    def updateItems(self):
        rects = self.getRects()
        for item, rect in rects.items():
            if isinstance(item, Widget):
                item.animate.geometry(rect, duration=300, silent=True)
            elif isinstance(item, Layout):
                item.formalGeometry = rect

    def updateSizes(self):
        pass

    def getRects(self) -> dict:
        pass
