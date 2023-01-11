from PyAsoka.GUI.Widgets.AWidget import AWidget, QPoint, QRect, QSize
from PyAsoka.src.Instruments.Menu import Menu, Button
from PyAsoka.GUI.Widgets.AMatrixMenu.AMatrixMenuButtonWidget import AMatrixMenuButtonWidget
from PyAsoka.GUI.Widgets.AMatrixMenu.AMatrixMenuUnitWidget import AMatrixMenuUnitWidget
from PyAsoka.Core.Logic.ALogicObject import ALogicObject


class AMatrixMenuElement:
    def __init__(self, callback, position: QPoint):
        self.position = position
        self.widget = None
        self.callback = callback

    def enter(self, action=None):
        self.callback(self.position)


class AMatrixMenuButton(AMatrixMenuElement):
    def __init__(self, button: Button, callback, position: QPoint = None):
        super(AMatrixMenuButton, self).__init__(callback, position)
        self.element = button


class AMatrixMenuUnit(AMatrixMenuElement):
    def __init__(self, menu: Menu, callback_open, callback_close, position: QPoint = None):
        super(AMatrixMenuUnit, self).__init__(callback_open, position)
        self.menu = menu
        self.elements = []
        self.logic = ALogicObject()
        for element in self.menu.elements:
            if isinstance(element, Button):
                mat_elem = AMatrixMenuButton(element, callback_open)
                self.elements.append(mat_elem)
            if isinstance(element, Menu):
                mat_elem = AMatrixMenuUnit(element, callback_open, callback_close)
                self.elements.append(mat_elem)
            self.logic.addFunction(f'[N {element.name}]',
                                   mat_elem.enter,
                                   call_type=ALogicObject.CallType.GUI)
        self.logic.addFunction(f'[N свернуть]',
                               callback_close,
                               call_type=ALogicObject.CallType.GUI)


class AMatrixMenuScene(AWidget):
    def __init__(self, parent: AWidget, block_size: QSize, indent: QPoint, horizontal: bool = True):
        super(AMatrixMenuScene, self).__init__(parent)
        self.resize(parent.size())
        self.block_size = block_size
        self.indent = indent
        self.horizontal = horizontal
        self.current_horizontal = horizontal
        self.matrix_size = QSize(0, 0)
        self.elements = []

    def paintEvent(self, event):
        return

    def update_size(self, x, y):
        if self.matrix_size.width() < x:
            self.matrix_size.setWidth(x)
        if self.matrix_size.height() < y:
            self.matrix_size.setHeight(y)
        self.resize(self.indent.x() + (self.matrix_size.width() + 1) * (self.block_size.width() + self.indent.x()),
                    self.indent.y() + (self.matrix_size.height() + 1) * (self.block_size.height() + self.indent.y()))

    def addElementsTo(self, elements, _from: QPoint, x, y):
        for element in elements:
            if isinstance(element, AMatrixMenuButton):
                element.widget = AMatrixMenuButtonWidget(self, element.element.name, element.element.icon, self.block_size)
            elif isinstance(element, AMatrixMenuUnit):
                element.widget = AMatrixMenuUnitWidget(self, element.menu.name, self.block_size)

            element.position = QPoint(x, y)
            pos = QPoint(self.indent.x() + x * (self.block_size.width() + self.indent.x()),
                         self.indent.y() + y * (self.block_size.height() + self.indent.y()))
            element.widget.setGeometry(QRect(pos, self.block_size), QRect(_from, self.block_size), 400)
            element.widget.show()
            self.elements.append(element)

            if self.current_horizontal:
                x += 1
            else:
                y += 1
        self.update_size(x, y)

    def load_menu(self, elements):
        if len(elements) > 0:
            for element in self.elements:
                element.widget.hide().ended.bind(element.widget.deleteLater)

        self.elements = []
        self.matrix_size = QSize(0, 0)
        x, y = 0, 0
        self.addElementsTo(elements, QPoint(self.indent), x, y)

    def open_unit(self, unit: AMatrixMenuUnit):
        bx, by = unit.position.x(), unit.position.y()
        self.current_horizontal = not self.current_horizontal
        if self.current_horizontal:
            x, y = bx + 1, by
        else:
            x, y = bx, by + 1

        self.addElementsTo(unit.elements, unit.widget.pos(), x, y)

    def close_unit(self, unit: AMatrixMenuUnit):
        for element in unit.elements:
            element.widget.hide().ended.bind(element.widget.deleteLater)
            self.elements.remove(element)
        self.current_horizontal = not self.current_horizontal
