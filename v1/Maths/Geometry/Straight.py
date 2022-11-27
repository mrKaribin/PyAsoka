import cv2

from PyAsoka.Maths.Geometry.APoint import APoint
from PyAsoka.Maths.Geometry.AVector import AVector
from PyAsoka.Graphics.Image import Image


class Straight:
    def __init__(self, arg1, arg2, arg3=None):
        self.x0 = 0
        self.y0 = 0
        self.p1 = 0
        self.p2 = 0
        self.A = 0
        self.B = 0
        self.C = 0
        if isinstance(arg1, APoint) and isinstance(arg2, APoint):
            self.from_2_points(arg1, arg2)
        elif isinstance(arg1, APoint) and isinstance(arg2, AVector):
            self.from_point_vector(arg1, arg2)
        elif None not in (arg1, arg2, arg3):
            self.from_coefficients(arg1, arg2, arg3)

    def from_2_points(self, point1: APoint, point2: APoint):
        vector = AVector(point1, point2)
        self.from_point_vector(point1, vector)

    def from_point_vector(self, point: APoint, vector: AVector):
        self.x0 = point.x
        self.y0 = point.y
        self.p1 = vector.x
        self.p2 = vector.y
        self.A = self.p2
        self.B = -self.p1
        self.C = self.y0 * self.p1 - self.x0 * self.p2
        # print(f'Straight: {self.A}x + {self.B}y + {self.C} = 0)')

    def from_coefficients(self, a, b, c):
        self.A = a
        self.B = b
        self.C = c

    def __and__(self, other):
        denominator = self.A * other.B - other.A * self.B
        if denominator != 0:
            x = round(-(self.C * other.B - other.C * self.B) / denominator)
            y = round(-(self.A * other.C - other.A * self.C) / denominator)
            return APoint(x, y)
        else:
            return None

    def getY(self, x):
        return (self.p2 * (x - self.x0) + self.y0 * self.p1) / self.p1

    def getX(self, y):
        return (self.p1 * (y - self.y0) + self.x0 * self.p2) / self.p2

    def draw(self, image: Image, thickness=2, color=(255, 0, 0)):
        points = []
        straights = [Straight(0, -1, 0), Straight(-1, 0, 0), Straight(0, -1, image.size().height - 2), Straight(-1, 0, image.size().width - 2)]
        for straight in straights:
            point = self & straight
            if point is not None and 0 <= point.x <= image.size().width and 0 <= point.y <= image.size().height:
                points.append(point)
            if len(points) > 1:
                break

        if len(points) > 1:
            print(f'Point1: {points[0].toPoint().arr()}')
            print(f'Point2: { points[1].toPoint().arr()}')
            cv2.line(image(), points[0].toPoint().arr(), points[1].toPoint().arr(), color, thickness)
