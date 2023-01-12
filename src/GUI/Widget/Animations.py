from PyAsoka.src.GUI.Animation.AnimationManager import Animation


class Animations:

    @staticmethod
    def loading(widget):
        anim1 = Animation(widget, b"alpha")
        anim1.setStartValue(1.0)
        anim1.setEndValue(0.5)
        anim1.setDuration(500)

        anim2 = Animation(widget, b"alpha")
        anim2.setStartValue(0.5)
        anim2.setEndValue(1.0)
        anim2.setDuration(500)

        anim1.ended.bind(anim2.start)
        anim2.ended.bind(anim1.start)
        return anim1
