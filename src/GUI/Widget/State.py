from PyAsoka.src.Core.Object import Object, ObjectMeta
from PyAsoka.src.Core.Signal import Signal, SignalType
from PyAsoka.src.GUI.Animation.Animation import Animation
from PyAsoka.src.GUI.Animation.SequentialAnimations import SequentialAnimations
from PyAsoka.src.GUI.Animation.ParallelAnimations import ParallelAnimations
from threading import Thread


class StateMeta(ObjectMeta):
    def __new__(mcs, name, bases, attrs, **extra_kwargs):
        attrs['_level_'] = 1 if 'level' not in extra_kwargs.keys() else extra_kwargs['level']
        return super().__new__(mcs, name, bases, attrs)


class State(Object, metaclass=StateMeta):

    enabled = Signal(Object)
    disabled = Signal(Object)

    def __init__(self, widget):
        super().__init__()
        self._widget_ = widget
        self.name = ''
        self._begin_animation_ = None
        self._animation_ = None
        self._end_animation_ = None
        self._task_thread_ = None

    def enable(self):
        self.enabled.emit(self)

        if self.haveBeginAnimation():
            begin_animation = self.startBeginAnimation()

            if self.haveAnimation():
                begin_animation.finished.connect(self.startAnimation)

        elif self.haveAnimation():
            self.startAnimation()

        if self.haveAsynchTask():
            self.startAsynchTask().start()

        if self.haveTask():
            self.task(self._widget_)

    def disable(self):
        if self.haveEndTask():
            self.endTask(self._widget_)

        if self.haveAnimation():
            self._animation_.stop()

        if self.haveEndAnimation():
            self.startEndAnimation()
        else:
            self.disabled.emit(self)

    def startBeginAnimation(self):
        animation = self.beginAnimation(self._widget_)
        self._begin_animation_ = animation
        animation.start()
        return animation

    def startAnimation(self):
        animation = self.animation(self._widget_)
        self._animation_ = animation
        animation.start()
        return animation

    def startEndAnimation(self):
        animation = self.endAnimation(self._widget_)
        self._end_animation_ = animation
        animation.finished.connect(lambda: self.disabled.emit(self), SignalType.SingleShotConnection)
        animation.start()
        return animation

    def startAsynchTask(self):
        thread = Thread(self.asynchTask, args=(self._widget_, ))
        self._task_thread_ = thread
        return thread

    def haveBeginAnimation(self):
        return not self.__class__.beginAnimation == State.beginAnimation

    def haveTask(self):
        return not self.__class__.task == State.task

    def haveAnimation(self):
        return not self.__class__.animation == State.animation

    def haveAsynchTask(self):
        return not self.__class__.asynchTask == State.asynchTask

    def haveEndAnimation(self):
        return not self.__class__.endAnimation == State.endAnimation

    def haveEndTask(self):
        return not self.__class__.endTask == State.endTask

    def beginAnimation(self, widget) -> Animation | SequentialAnimations | ParallelAnimations:
        pass

    def task(self, widget):
        pass

    def animation(self, widget) -> Animation | SequentialAnimations | ParallelAnimations:
        pass

    def asynchTask(self, widget):
        pass

    def endAnimation(self, widget) -> Animation | SequentialAnimations | ParallelAnimations:
        pass

    def endTask(self, widget):
        pass
