from enum import Enum, auto


class Size:
    def __init__(self, w: int, h: int):
        self.width = w
        self.height = h

    def arr(self):
        return [self.width, self.height]


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    def set(self, x: int, y: int):
        self.x = x
        self.y = y

    def reverse(self):
        self.x, self.y = self.y, self.x

    def draw(self, image, color=(0, 0, 255), size: int = 5):
        from cv2 import circle, FILLED
        from PyAsoka.Graphics.Image import Image
        if isinstance(image, Image):
            circle(image(), (self.x, self.y), size, color, FILLED)

    def toAPoint(self):
        from PyAsoka.Maths.Geometry.APoint import APoint
        return APoint(self.x, self.y)

    def arr(self):
        return [self.x, self.y]

    @staticmethod
    def average(points: list):
        summa = Point()
        count = 0
        for point in points:
            if point is not None:
                summa.x += point.x
                summa.y += point.y
                count += 1
        return Point(summa.x // count, summa.y // count) if summa.x != 0 or summa.y != 0 else None


class RelativePoint(Point):
    def __init__(self, x: float, y: float, imsize: Size = None):
        self.x = 0
        self.y = 0
        self.rel_x = x
        self.rel_y = y
        self.imsize = imsize
        self.__recalculate__()

    def set_multiplier(self, x: float, y: float):
        self.rel_x = x
        self.rel_y = y
        self.__recalculate__()

    def set_imsize(self, size: Size):
        self.imsize = size
        self.__recalculate__()

    def __recalculate__(self):
        self.x = int(self.imsize.width * self.rel_x)
        self.y = int(self.imsize.height * self.rel_y)


class Rect:
    def __init__(self, *args):
        self.topLeft = Point(0, 0)
        self.topRight = Point(0, 0)
        self.bottomLeft = Point(0, 0)
        self.bottomRight = Point(0, 0)
        self.top = 0
        self.bottom = 0
        self.left = 0
        self.right = 0
        self.size = Size(0, 0)

        if len(args) == 2:
            self.from_2p(*args)
        elif len(args) == 3:
            self.from_2p_ang(*args)
        elif len(args) == 4:
            self.from_4p(*args)

    def from_2p(self, base: Point, end: Point):
        self.topLeft = base
        self.topRight = Point(end.x, base.y)
        self.bottomLeft = Point(base.x, end.y)
        self.bottomRight = end
        self.size = Size(self.topRight.x - self.topLeft.x, self.bottomLeft.y - self.topLeft.y)
        self.__update__()

    def from_4p(self, top_left: Point, top_right: Point, bottom_left: Point, bottom_right: Point):
        self.topLeft = top_left
        self.topRight = top_right
        self.bottomLeft = bottom_left
        self.bottomRight = bottom_right
        self.size = Size(self.topRight.x - self.topLeft.x, self.bottomLeft.y - self.topLeft.y)  # not correct ToDo
        self.__update__()

    def from_2p_ang(self, base, end, angle):
        self.__update__()

    def __update__(self):
        self.top = self.topLeft.y
        self.bottom = self.bottomRight.y
        self.left = self.topLeft.x
        self.right = self.bottomRight.x
