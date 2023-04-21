from PyAsoka.src.GUI.Layouts.Layout import Layout, Widget, QSize, QRect
from PyAsoka.src.Debug.Exceptions import Exceptions
from PyAsoka.Asoka import Asoka

from enum import Enum, auto


class Size:
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height

    def toQSize(self):
        return QSize(self.width, self.height)


class LinearLayout(Layout):
    class Type(Enum):
        HORIZONTAL = auto()
        VERTICAL = auto()

    def __init__(self, type: Type, parent=None):
        super().__init__(parent)
        self._type_ = type
        self._stretch_ = QSize()

    @property
    def type(self):
        return self._type_

    def getRects(self):
        isHorizontal = self.type == LinearLayout.Type.HORIZONTAL
        isVertical = not isHorizontal
        Alignment = Asoka.Alignment
        totalSize, totalMinimumSize, totalMaximumSize, stretch = self.updateSizes()
        size = self.availableSize
        rects = {}
        x = self.margin
        y = self.margin

        if self.size.width() > size.width():
            if se

        if isHorizontal:
            if self.size.width() > size.width():
                print('size PIZDEC')

        for item in self.items:
            if isinstance(item, (Layout, Widget)):
                if isHorizontal:
                    width, height = item.formalSize.width(), item.formalSize.height()
                    if item.stretchY:
                        height = size.height() - self.margin * 2
                        if item.aspectRatio:
                            arx, ary = item.aspectRatio
                            width = int(height / ary * arx)

                    if item.alignment == Alignment.AlignLeft:
                        rects[item] = QRect(x, y, width, height)
                    if item.alignment in (Alignment.AlignHCenter, Alignment.AlignVCenter, Alignment.AlignCenter):
                        rects[item] = QRect(x, (size.height() - height) // 2, width, height)
                    x += item.formalSize.width()
                    x += self.spacing
                elif isVertical:
                    width, height = item.formalSize.width(), item.formalSize.height()
                    if item.stretchX:
                        width = size.width() - self.margin * 2
                        if item.aspectRatio:
                            arx, ary = item.aspectRatio
                            height = int(width / arx * ary)

                    if item.alignment == Alignment.AlignLeft:
                        rects[item] = QRect(x, y, width, height)
                    if item.alignment in (Alignment.AlignHCenter, Alignment.AlignVCenter, Alignment.AlignCenter):
                        rects[item] = QRect((size.width() - width) // 2, y, width, height)
                    y += item.formalSize.height()
                    y += self.spacing

        return rects

    def updateSizes(self):
        isHorizontal = self.type == LinearLayout.Type.HORIZONTAL
        isVertical = not isHorizontal

        totalSize = Size(self.margin * 2, self.margin * 2)
        totalMinimumSize = Size(self.margin * 2, self.margin * 2)
        totalMaximumSize = Size(self.margin * 2, self.margin * 2)
        stretch = Size()

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

                if isVertical:
                    totalSize.height += item.formalSize.height() + self.spacing
                    totalSize.width = max(totalSize.width, item.formalSize.width())
                    totalMinimumSize.height += item.minSize.height() + self.spacing
                    totalMinimumSize.width = max(totalMinimumSize.width, item.minSize.width())
                    totalMaximumSize.height += item.maxSize.height() + self.spacing
                    totalMaximumSize.width = max(totalMaximumSize.width, item.maxSize.width())

        if isHorizontal:
            totalSize.width -= self.spacing
            totalMinimumSize.width -= self.spacing
            totalMaximumSize.width -= self.spacing
        if isVertical:
            totalSize.height -= self.spacing
            totalMinimumSize.height -= self.spacing
            totalMaximumSize.height -= self.spacing

        print('Total size', totalSize.width, totalSize.height)
        print('Total minimum size', totalMinimumSize.width, totalMinimumSize.height)
        print('Total maximum size', totalMaximumSize.width, totalMaximumSize.height)
        print('')

        self.size = totalSize.toQSize()
        self.minSize = totalMinimumSize.toQSize()
        self.maxSize = totalMaximumSize.toQSize()
        self._stretch_ = stretch
        return totalSize, totalMinimumSize, totalMaximumSize, stretch
