from PyAsoka.GUI.Widgets.AWidget import AWidget, Qt, QPaintEvent, QPoint, QSize, QRect, QPen, QBrush, Qt
from PyAsoka.GUI.Widgets.AMatrixMenu.AMatrixMenuScene import AMatrixMenuScene, AMatrixMenuUnit, AMatrixMenuButton
from PyAsoka.Instruments.Menu import Menu, Element, Button
from PyAsoka.GUI.Styles import Styles, Color
from PyAsoka.GUI.API import API

from PySide6.QtGui import QKeyEvent


class AMatrixMenu(AWidget):
    def __init__(self, block_size: QSize = QSize(120, 120), indent: QPoint = QPoint(30, 30),
                 parent: AWidget = None, menu: Menu = None, **kwargs):
        super(AMatrixMenu, self).__init__(parent, style=Styles.overlayFullscreen(), animated=False, **kwargs)

        self.scene = AMatrixMenuScene(self, block_size, indent)
        self.current = None
        self.unites = []
        self.current_position = QPoint(0, 0)
        self.menu = None
        self.unit = None
        self.cursor_position = QPoint()
        self.update_cursor()
        API.Keyboard.pressed.bind(self.key_pressed)

        self.scene.move(QPoint((self.width() - self.scene.width()) // 2, (self.height() - self.scene.height()) // 2), duration=None)
        if menu is not None and isinstance(menu, Menu) and len(menu.elements) > 0:
            self.setMenu(menu)

    def update_cursor(self):
        self.cursor_position = QPoint(self.width() // 2 - self.scene.block_size.width() // 2,
                                      self.height() // 2 - self.scene.block_size.height() // 2)

    def setMenu(self, menu: Menu):
        self.menu = menu
        self.unites = []
        self.current_position = QPoint(0, 0)
        self.unit = AMatrixMenuUnit(menu, self.enter_position, self.close)
        self.unit.logic.enable()
        self.scene.load_menu(self.unit.elements)
        self.current = self.scene.elements[0]
        self.update_cursor()
        self.change_position(0, 0, None)

    def paintEvent(self, event: QPaintEvent):
        self.update_cursor()
        painter = self.__get_painter__()
        indent = self.scene.indent.x() // 3
        position = QPoint(self.cursor_position.x() - indent, self.cursor_position.y() - indent)
        size = QSize(self.scene.block_size.width() + indent * 2, self.scene.block_size.height() + indent * 2)
        painter.setPen(QPen(self.colors.frame, 2))
        painter.drawRoundedRect(QRect(position, size), 20, 20)

        painter.setPen(QPen(self.colors.background))
        painter.setBrush(QBrush(self.colors.background))
        painter.drawRect(QRect(QPoint(0, 0), self.size()))

    def current_unite(self):
        return self.unites[-1] if len(self.unites) > 0 else self.unit

    def change_position(self, x, y, duration=250):
        if (element := self.find_element_by_position(x, y)) is not None:
            self.current_position.setX(x)
            self.current_position.setY(y)
            self.current = element
            wgt_pos = QPoint(self.scene.indent.x() + self.current_position.x() * (self.scene.block_size.width() + self.scene.indent.x()),
                             self.scene.indent.y() + self.current_position.y() * (self.scene.block_size.height() + self.scene.indent.y()))
            delta = QPoint(self.cursor_position.x() - (wgt_pos.x() + self.scene.pos().x()),
                           self.cursor_position.y() - (wgt_pos.y() + self.scene.pos().y()))
            position = QPoint(self.scene.pos().x() + delta.x(), self.scene.pos().y() + delta.y())
            self.scene._animations_geometry_.clear()
            return self.scene.move(position, duration)

    def find_element_by_position(self, x, y):
        for element in self.scene.elements:
            if element.position.x() == x and element.position.y() == y:
                return element
        return None

    def key_pressed(self, key):
        kb = API.Keyboard
        if key == kb.Simbol('w') and not self.scene.current_horizontal:
            self.up()
        if key == kb.Simbol('s'):
            if not self.scene.current_horizontal:
                self.down()
            elif isinstance(self.current, AMatrixMenuUnit):
                self.enter()
        if key == kb.Simbol('a') and self.scene.current_horizontal:
            self.left()
        if key == kb.Simbol('d'):
            if self.scene.current_horizontal:
                self.right()
            elif isinstance(self.current, AMatrixMenuUnit):
                self.enter()
        if key == kb.Key.enter or key == kb.Simbol('f'):
            self.enter()
        if key == kb.Simbol('e'):
            self.close()
        if key == kb.Simbol('q'):
            self.exit()

    def up(self):
        self.change_position(self.current_position.x(), self.current_position.y() - 1)
        if self.current == self.current_unite():
            self.close()

    def down(self):
        self.change_position(self.current_position.x(), self.current_position.y() + 1)

    def left(self):
        self.change_position(self.current_position.x() - 1, self.current_position.y())
        if self.current == self.current_unite():
            self.close()

    def right(self):
        self.change_position(self.current_position.x() + 1, self.current_position.y())

    def enter(self):
        if isinstance(self.current, AMatrixMenuUnit):
            self.current_unite().logic.disable()
            self.unites.append(self.current)
            self.scene.open_unit(self.current)
            self.current.logic.enable()
            if self.scene.current_horizontal:
                self.right()
            else:
                self.down()
        elif isinstance(self.current, AMatrixMenuButton):
            self.current.element.clicked()
            self.vanishing()

    def enter_position(self, position: QPoint):
        self.change_position(position.x(), position.y()).ended.bind(self.enter)

    def close(self, action=None):
        if len(self.unites) > 0:
            unit = self.unites.pop(-1)
            unit.logic.disable()
            self.scene.close_unit(unit)
            self.change_position(unit.position.x(), unit.position.y())
            self.current_unite().logic.enable()

    def exit(self):
        self.vanishing()

    def deleteLater(self):
        self.unit.logic.disable()
        super(AMatrixMenu, self).deleteLater()


