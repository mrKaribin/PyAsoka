
class Point:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def set(self, x: int, y: int):
        self.x = x
        self.y = y

    def reverse(self):
        self.x, self.y = self.y, self.x

    def toPoint(self):
        from PyAsoka.src.Graphics.Geometry import Point
        return Point(self.x, self.y)

    def arr(self):
        return [self.x, self.y, self.z]
