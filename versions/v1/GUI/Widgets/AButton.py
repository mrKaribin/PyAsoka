from PyAsoka.GUI.Widgets.AWidget import AnimationManager
from PyAsoka.GUI.Widgets.ATextView import ATextView
from PyAsoka.GUI.Styles import Styles, Colors
from PyAsoka.GUI.Color import Color


class AButton(ATextView):
    def __init__(self, text, **kwargs):
        super(AButton, self).__init__(text, clickable=True, style=Styles.close(), round_size=10, **kwargs)
        self._click_animations_ = AnimationManager()
        self.setTextBold(True)
        self.clicked.bind(self.click_animation)

    def click_animation(self):
        self._click_animations_.clear()
        self._click_animations_.add(self.setColor(self.colors.frame, Colors.Frame.focus(), 150, autorun=False))
        self._click_animations_.add(self.setColor(self.colors.frame, self.style.frame, 150, autorun=False))
        self._click_animations_.start()

    def enterEvent(self, event):
        self._animations_color_.clear()
        color = self.colors.background
        self.setColor(color, Color(color.red() - 10, color.green() - 10, color.blue() - 10, color.alpha()), 150)

    def leaveEvent(self, event):
        self.setColor(self.colors.background, self.style.background, 150)
