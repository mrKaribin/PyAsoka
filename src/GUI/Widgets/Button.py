from PyAsoka.src.GUI.Animation.Animation import Animation
from PyAsoka.src.GUI.Animation.SequentialAnimations import SequentialAnimations
from PyAsoka.src.GUI.Widgets.TextView import TextView
from PyAsoka.src.GUI.Style.Styles import Styles, Colors, Color
from PyAsoka.Asoka import Asoka


class Button(TextView):
    def __init__(self, text: str, **kwargs):
        super().__init__(text.upper(), text_bold=True, clickable=True, style=Styles.Button, **kwargs)
        self._click_animation_ = None
        self._frame_animation_ = None
        self.text.font.setBold(True)
        self.clicked.connect(self.click_animation)

    def click_animation(self):
        if self._click_animation_ is not None:
            self._click_animation_.stop()
        self._click_animation_ = SequentialAnimations(
            Animation(self.style(), b'frame', self.style.current.frame, Colors.Frame.focus(), duration=150),
            Animation(self.style(), b'frame', Colors.Frame.focus(), self.style.current.frame, duration=150)
        )
        self._click_animation_.start()

    def enterEvent(self, event):
        if self._frame_animation_ is not None:
            self._frame_animation_.stop()
        color = self.style.default.background
        self._frame_animation_ = self.animate.color('background', Color(color.red() - 10, color.green() - 10, color.blue() - 10, color.alpha()), duration=150)

    def leaveEvent(self, event):
        if self._frame_animation_ is not None:
            self._frame_animation_.stop()
        self._frame_animation_ = self.animate.color('background', self.style.default.background, duration=150)
