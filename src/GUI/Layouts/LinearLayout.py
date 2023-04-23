from PyAsoka.src.GUI.Layouts.Layout import Layout, Widget, QSize, QRect, QPoint, Size, Point
from PyAsoka.src.Debug.Exceptions import Exceptions
from PyAsoka.Asoka import Asoka

from enum import Enum, auto


class LinearLayout(Layout):
    class Type(Enum):
        HORIZONTAL = auto()
        VERTICAL = auto()

    def __init__(self, type: Type, parent):
        super().__init__(parent)
        self._type_ = type
        self._sections_ = QPoint()

    @property
    def type(self):
        return self._type_

    @property
    def sections(self) -> QPoint:
        return self._sections_

    def getRects(self):
        isHorizontal = self.type == LinearLayout.Type.HORIZONTAL
        isVertical = not isHorizontal
        Alignment = Asoka.Alignment
        self.updateSizes()
        available = self.availableSize
        freeSpace = Size(0, 0)
        additionalSize = Size()
        newSize = QSize(available.width(), available.height())
        rects = {}
        x = self.margin
        y = self.margin

        # Рассчет занятого пространства базового виджета и потребности в его масштабировании
        if self.contentSize.width() > available.width():
            if self.contentSize.width() <= self.maxSize.width():
                newSize.setWidth(self.contentSize.width())
            else:
                newSize.setWidth(self.maxSize.width())
                freeSpace.width = self.maxSize.width() - self.contentSize.width()
        elif self.contentSize.width() < available.width():
            if self.constrict.x:
                newSize.setWidth(self.contentSize.width())
            else:
                freeSpace.width = available.width() - self.contentSize.width()
                additionalSize.width = freeSpace.width // self.sections.x()

        if self.contentSize.height() > available.height():
            if self.contentSize.height() <= self.maxSize.height():
                newSize.setHeight(self.contentSize.height())
            else:
                newSize.setHeight(self.maxSize.height())
                freeSpace.height = self.maxSize.height() - self.contentSize.height()
        elif self.contentSize.height() < available.height():
            if self.constrict.y:
                newSize.setHeight(self.contentSize.height())
            else:
                freeSpace.height = available.height() - self.contentSize.height()
                additionalSize.height = freeSpace.height // self.sections.y()

        if available.width() != newSize.width() or available.height() != newSize.height():
            if self.widget is not None:
                rects[self.widget] = QRect(self.widget.formalPosition, newSize)
            else:
                self.formalSize = newSize

        print('Widget:', self.widget, 'stretch:', (self.stretch.x, self.stretch.y))
        print('Content size: ', self.contentSize)
        print('Available size: ', self.availableSize)
        print('New size: ', newSize)
        print('')

        # Рассчет координат дочерних виджетов
        for item in self.items:
            if isinstance(item, (Layout, Widget)):
                if isHorizontal:
                    width, height = item.formalSize.width(), item.formalSize.height()
                    if item.stretch.y:
                        height = available.height() - self.margin * 2
                        if isinstance(item, Widget) and item.aspectRatio:
                            arx, ary = item.aspectRatio
                            width = int(height / ary * arx)
                    if item.stretch.x:
                        width = item.formalSize.width() + additionalSize.width

                    if item.alignment == Alignment.AlignLeft:
                        rects[item] = QRect(x, y, width, height)
                    if item.alignment in (Alignment.AlignHCenter, Alignment.AlignVCenter, Alignment.AlignCenter):
                        rects[item] = QRect(x, (available.height() - height) // 2, width, height)
                    x += item.formalSize.width()
                    x += self.spacing
                elif isVertical:
                    width, height = item.formalSize.width(), item.formalSize.height()
                    if item.stretch.x:
                        width = available.width() - self.margin * 2
                        if isinstance(item, Widget) and item.aspectRatio:
                            arx, ary = item.aspectRatio
                            height = int(width / arx * ary)
                    if item.stretch.y:
                        height = item.formalSize.height() + additionalSize.height

                    if item.alignment == Alignment.AlignLeft:
                        rects[item] = QRect(x, y, width, height)
                    if item.alignment in (Alignment.AlignHCenter, Alignment.AlignVCenter, Alignment.AlignCenter):
                        rects[item] = QRect((available.width() - width) // 2, y, width, height)
                    y += item.formalSize.height()
                    y += self.spacing
            if isinstance(item, Layout.Spacing):
                if isHorizontal:
                    x += additionalSize.width
                if isVertical:
                    y += additionalSize.height

        return rects

    def updateSizes(self):
        isHorizontal = self.type == LinearLayout.Type.HORIZONTAL
        isVertical = not isHorizontal

        totalSize = Size(self.margin * 2, self.margin * 2)
        totalMinimumSize = Size(self.margin * 2, self.margin * 2)
        totalMaximumSize = Size(self.margin * 2, self.margin * 2)
        stretch = Point()

        # for layout in self.layouts():
        #     layout.updateSizes()

        for item in self.items:
            if isinstance(item, (Layout, Widget)):
                if isHorizontal:
                    totalSize.width += item.formalSize.width() + self.spacing
                    totalSize.height = max(totalSize.height, item.formalSize.height())
                    totalMinimumSize.width += item.minSize.width() + self.spacing
                    totalMinimumSize.height = max(totalMinimumSize.height, item.minSize.height())
                    totalMaximumSize.width += item.maxSize.width() + self.spacing
                    totalMaximumSize.height = max(totalMaximumSize.height, item.maxSize.height())
                    if item.stretch.x:
                        stretch.x += int(item.stretch.x)

                if isVertical:
                    totalSize.height += item.formalSize.height() + self.spacing
                    totalSize.width = max(totalSize.width, item.formalSize.width())
                    totalMinimumSize.height += item.minSize.height() + self.spacing
                    totalMinimumSize.width = max(totalMinimumSize.width, item.minSize.width())
                    totalMaximumSize.height += item.maxSize.height() + self.spacing
                    totalMaximumSize.width = max(totalMaximumSize.width, item.maxSize.width())
                    if item.stretch.y:
                        stretch.y += int(item.stretch.y)

            elif isinstance(item, Layout.Spacing):
                stretch.x += item.x
                stretch.y += item.y

        if isHorizontal:
            totalSize.width -= self.spacing
            totalMinimumSize.width -= self.spacing
            totalMaximumSize.width -= self.spacing
        if isVertical:
            totalSize.height -= self.spacing
            totalMinimumSize.height -= self.spacing
            totalMaximumSize.height -= self.spacing

        # print('Total size', totalSize.width, totalSize.height)
        # print('Total minimum size', totalMinimumSize.width, totalMinimumSize.height)
        # print('Total maximum size', totalMaximumSize.width, totalMaximumSize.height)
        # print('')

        self.contentSize = totalSize.toQSize()
        self.minContentSize = totalMinimumSize.toQSize()
        self.maxContentSize = totalMaximumSize.toQSize()
        self._sections_ = stretch.toQPoint()
        return totalSize, totalMinimumSize, totalMaximumSize, stretch
