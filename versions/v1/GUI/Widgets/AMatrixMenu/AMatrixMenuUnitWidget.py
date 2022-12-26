import PyAsoka.Asoka as a

from PyAsoka.GUI.Widgets.AWidget import AWidget, QPaintEvent, QPoint, QRect, QSize
from PyAsoka.GUI.Widgets.ATextView import ATextView
from PyAsoka.GUI.Widgets.AIconView import AIconView
from PyAsoka.GUI.Styles import Styles, Style, Color

from PySide6.QtCore import Qt, Property
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from PySide6.QtWidgets import QVBoxLayout


class AMatrixMenuUnitWidget(AWidget):
    def __init__(self, parent, text, size: QSize):
        super(AMatrixMenuUnitWidget, self).__init__(parent, clickable=True,
                                                    style=Styles.toolWindow())
        # AStyle(frame=AColor(50, 120, 110, 220), background=AColor(48, 98, 107, 220))
        self.setFixedSize(size)
        self.text = ATextView(text, parent=self)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setTextBold(True)
        self.text.setTextSize(int(self.size().width() * 0.09))
        self.icon = AIconView(f'{a.dir.images()}/default_menu.png', parent=self, style=Styles.frameWidget())
        self.icon.setFixedSize(size.height() // 2, size.height() // 2)
        lay = QVBoxLayout(self)
        lay.addStretch(1)
        lay.addWidget(self.icon, alignment=Qt.AlignCenter)
        lay.addWidget(self.text)
        lay.addStretch(1)
        lay.setSpacing(0)
        self.setLayout(lay)

    def paintEvent(self, event: QPaintEvent):
        if self.__is_content_visible__():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(self.colors.frame, 2))
            painter.setBrush(QBrush(self.colors.background))
            painter.drawRoundedRect(QRect(QPoint(0, 0), self.size()), self.size().height() // 4, self.size().height() // 4)
