from PyAsoka.src.Core.Signal import Signal
from PySide6.QtCore import QParallelAnimationGroup, QAnimationGroup, QPropertyAnimation


class ParallelAnimations(QParallelAnimationGroup):
    def __init__(self, *args, parent=None):
        super().__init__(parent)

        for animation in args:
            if isinstance(animation, QPropertyAnimation) or isinstance(animation, QAnimationGroup):
                self.addAnimation(animation)

        self.ended = Signal(ParallelAnimations)
        self.finished.connect(lambda: self.ended(self))
