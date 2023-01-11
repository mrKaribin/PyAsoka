from PyAsoka.src.GUI.Animation import Animation, QPropertyAnimation, Signal
from PySide6.QtCore import QObject


class AnimationManager(QObject):
    def __init__(self):
        super().__init__(None)
        # public
        self.queue = []
        self.parallel = []
        self.current = []
        self.queue_is_run = False
        self.parallel_is_run = False

        # signals
        self.ended_queue = Signal(AnimationManager)
        self.ended_parallel = Signal(AnimationManager)

    def timeRemaining(self):
        time = 0
        for animation in self.queue:
            time += animation.timeRemaining()
        return time

    def isRun(self):
        return self.current is not None

    def add(self, animation: QPropertyAnimation, _type: Animation.Type = Animation.Type.QUEUE):
        if _type == Animation.Type.QUEUE:
            self.queue.append(animation)
        else:
            self.parallel.append(animation)
        return self

    def start(self):
        if len(self.queue) and not self.queue_is_run:
            self.start_queue()
        if len(self.parallel):
            self.start_parallel()
        return self

    def start_queue(self):
        if len(self.queue) > 0:
            self.queue_is_run = True
            self._start_animation_(self.queue.pop(0), Animation.Type.QUEUE)
        else:
            self.queue_is_run = False
            self.ended_queue(self)

    def start_parallel(self):
        while len(self.parallel):
            self.parallel_is_run = True
            self._start_animation_(self.parallel.pop(0), Animation.Type.PARALLEL)

    def _start_animation_(self, animation: QPropertyAnimation, anim_type: Animation.Type):
        animation.ended.bind(self.remove)
        if anim_type == Animation.Type.QUEUE:
            animation.ended.bind(self.next_in_queue)
        if anim_type == Animation.Type.PARALLEL:
            animation.ended.bind(self.ended_in_parallel)
        animation.start()
        self.current.append(animation)

    def _check_trash_(self):
        for animation in self.current:
            if animation.state() in (Animation.State.Stopped, Animation.State.Paused):
                self.current.remove(animation)
                self._check_trash_()

    def next_in_queue(self, last: QPropertyAnimation):
        self._check_trash_()
        self.start_queue()

    def ended_in_parallel(self):
        if len(self.parallel) == 0:
            self.parallel_is_run = False
            self._check_trash_()
            self.ended_parallel(self)

    def clear(self):
        self.queue = []
        self.parallel = []
        self.queue_is_run = False
        for animation in self.current:
            animation.stop()
        self.current = []

    def remove(self, animation: QPropertyAnimation):
        self.current.remove(animation)
