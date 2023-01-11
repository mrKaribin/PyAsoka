import math

from PyAsoka.src.Geometry.Point import Point


class AVector:
    def __init__(self, arg1=0, arg2=0, arg3=0):
        self.x = 0
        self.y = 0
        self.z = 0

        if isinstance(arg1, Point) and isinstance(arg2, Point):
            self.from_points(arg1, arg2)
        elif isinstance(arg1, float) and isinstance(arg2, float) and isinstance(arg3, float):
            self.from_values(arg1, arg2, arg3)
        elif isinstance(arg1, int) and isinstance(arg2, int) and isinstance(arg3, int):
            self.from_values(arg1, arg2, arg3)
        else:
            raise Exception(f'Получен неверный тип данных аргументов: {type(arg1), type(arg2), type(arg3)}')

    def from_points(self, point1: Point, point2: Point):
        self.x = point2.x - point1.x
        self.y = point2.y - point1.y
        self.z = point2.z - point1.z

    def from_values(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def copy(self):
        return AVector(self.x, self.y, self.z)

    # сложение векторов
    def __add__(self, other):
        if isinstance(other, AVector):
            return AVector(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z
            )
        else:
            raise Exception(f'Получен неверный тип данных: {other}')

    # вычитание векторов
    def __sub__(self, other):
        if isinstance(other, AVector):
            return AVector(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z
            )
        else:
            raise Exception(f'Получен неверный тип данных: {other}')

    # произведение векторов
    def __mul__(self, other):
        pass

    # модуль вектора
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    # скалярное произведение векторов
    def __pow__(self, other):
        if isinstance(other, AVector):
            return self.x * other.x + self.y * other.y + self.z * other.z
        elif isinstance(other, int):
            return AVector(self.x ** other, self.y ** other, self.z ** other)
        else:
            raise Exception(f'Получен неверный тип данных: {other}')

    # угол между данным и другим вектором
    def angle(self, vector):
        if isinstance(vector, AVector):
            angle = math.degrees(math.atan2(self.x * vector.y - self.y * vector.x, self.x * vector.x + self.y * vector.y))
            return angle
        else:
            raise Exception(f'Получен неверный тип данных: {type(vector)}')

    # вращение вектора на angle градусов в 2D пространстве
    def rotate(self, angle):
        cs = math.cos(math.radians(angle))
        sn = math.sin(math.radians(angle))
        x = self.x * cs - self.y * sn
        y = self.x * sn + self.y * cs
        self.x, self.y = x, y
        return self

    def unit(self):
        return AVector(self.x / self.length(), self.y / self.length(), self.z / self.length())
