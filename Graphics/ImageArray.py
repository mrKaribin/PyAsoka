import math
import os
import cv2
import numpy
import PIL.Image as PImage

from enum import Enum, auto
from PyAsoka.Graphics.Geometry import Point, Size


def hsv_to_gray(image):
    img = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def gray_to_hsv(image):
    img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


class ImageArray:
    class Type(Enum):
        CV2 = auto()
        PIL = auto()

    class Scheme(Enum):
        RGB = auto()
        BGR = auto()
        HSV = auto()
        LAB = auto()
        GRAY = auto()

    class Channel(Enum):
        RED = auto()
        GREEN = auto()
        BLUE = auto()
        HUE = auto()
        SATURATION = auto()
        VALUE = auto()
        GRAY = auto()
        LAB_L = auto()
        LAB_A = auto()
        LAB_B = auto()

        @staticmethod
        def channels():
            ch = ImageArray.Channel
            return {
                ImageArray.Scheme.HSV: [ch.HUE, ch.SATURATION, ch.VALUE],
                ImageArray.Scheme.RGB: [ch.RED, ch.GREEN, ch.BLUE],
                ImageArray.Scheme.BGR: [ch.BLUE, ch.GREEN, ch.RED],
                ImageArray.Scheme.LAB: [ch.LAB_L, ch.LAB_A, ch.LAB_B],
                ImageArray.Scheme.GRAY: [ch.GRAY],
            }

    class BorderType(Enum):
        CUSTOM = auto()
        STRAIGHT = auto()
        ARC = auto()

    class Direction(Enum):
        TOP = auto()
        BOTTOM = auto()
        LEFT = auto()
        RIGHT = auto()

    class convert:
        @staticmethod
        def type(image, _from, _to):
            data = image.data if isinstance(image, ImageArray) else image
            if _from == ImageArray.Type.CV2:
                if _to == ImageArray.Type.PIL:
                    return PImage.fromarray(data)

            if _from == ImageArray.Type.PIL:
                if _to == ImageArray.Type.CV2:
                    return cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)

        @staticmethod
        def scheme(image, _from, _to):
            tp = ImageArray.Scheme
            result = None
            scheme = None
            data = image.data if isinstance(image, ImageArray) else image

            function = {
                tp.BGR: {
                    tp.RGB: lambda: cv2.cvtColor(data, cv2.COLOR_BGR2RGB),
                    tp.HSV: lambda: cv2.cvtColor(data, cv2.COLOR_BGR2HSV),
                    tp.GRAY: lambda: cv2.cvtColor(data, cv2.COLOR_BGR2GRAY),
                    tp.LAB: lambda: cv2.cvtColor(data, cv2.COLOR_BGR2LAB)
                },
                tp.RGB: {
                    tp.BGR: lambda: cv2.cvtColor(data, cv2.COLOR_RGB2BGR),
                    tp.HSV: lambda: cv2.cvtColor(data, cv2.COLOR_RGB2HSV),
                    tp.GRAY: lambda: cv2.cvtColor(data, cv2.COLOR_RGB2GRAY),
                    tp.LAB: lambda: cv2.cvtColor(data, cv2.COLOR_RGB2LAB)
                },
                tp.HSV: {
                    tp.RGB: lambda: cv2.cvtColor(data, cv2.COLOR_HSV2RGB),
                    tp.BGR: lambda: cv2.cvtColor(data, cv2.COLOR_HSV2BGR),
                    tp.GRAY: lambda: hsv_to_gray(data),
                    tp.LAB: lambda: cv2.cvtColor(cv2.cvtColor(data, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2LAB)
                },
                tp.GRAY: {
                    tp.BGR: lambda: cv2.cvtColor(data, cv2.COLOR_GRAY2BGR),
                    tp.RGB: lambda: cv2.cvtColor(data, cv2.COLOR_GRAY2RGB),
                    tp.HSV: lambda: gray_to_hsv(data),
                    tp.LAB: lambda: cv2.cvtColor(cv2.cvtColor(data, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2LAB)
                },
                tp.LAB: {
                    tp.BGR: lambda: cv2.cvtColor(data, cv2.COLOR_LAB2BGR),
                    tp.RGB: lambda: cv2.cvtColor(data, cv2.COLOR_LAB2RGB),
                    tp.HSV: lambda: cv2.cvtColor(cv2.cvtColor(data, cv2.COLOR_LAB2BGR), cv2.COLOR_BGR2HSV),
                    tp.GRAY: lambda: cv2.cvtColor(cv2.cvtColor(data, cv2.COLOR_LAB2BGR), cv2.COLOR_BGR2GRAY)
                }
            }

            result = function[_from][_to]()
            scheme = _to
            from PyAsoka.Graphics.Image import Image
            if isinstance(image, ImageArray):
                image.data = result
                if isinstance(image, Image):
                    image.scheme = scheme
                return image
            else:
                return result

    def __init__(self, data):
        self.data = data
        self._array_ = None

    def __call__(self):
        return self.data

    def __getitem__(self, item):
        simple = True
        if isinstance(item, tuple):
            for i in item:
                if isinstance(i, slice):
                    simple = False
        elif isinstance(item, slice):
            simple = False
        elif isinstance(item, int):
            pass
        else:
            raise Exception('Передан неверный тип данных')

        if simple:
            raise Exception('Запрещен доступ к пикселям через индекс. Используйте для этого array(), update().')
        else:
            return self.data[item]

    def from_file(self, path):
        if os.path.exists(path):
            self.data = cv2.imread(path)
            return self
        else:
            raise Exception('Не найден файл изображения')

    def size(self):
        return Size(self.width(), self.height())

    def width(self):
        return self.data.shape[1] if self.data is not None else 0

    def height(self):
        return self.data.shape[0] if self.data is not None else 0

    def show(self, win_name: str = 'Image', stream: bool = False):
        cv2.imshow(win_name, self.data)
        cv2.waitKey(1 if stream else 0)

    def flip(self, horizontal=True, vertical=False):
        if horizontal:
            self.data = cv2.flip(self.data, 1)
        if vertical:
            self.data = cv2.flip(self.data, 2)
        return self

    def resize(self, w: int = 0, h: int = 0, scale=None):
        if isinstance(w, Size):
            w, h = w.arr()

        if scale is None:
            self.data = cv2.resize(self.data, (w, h), interpolation=cv2.INTER_AREA)
        else:
            self.data = cv2.resize(self.data, (int(self.width() * scale), int(self.height() * scale)))
        return self

    def shift(self, x, y):
        h, w = self.data.shape[:2]
        translation_matrix = numpy.float32([[1, 0, x], [0, 1, y]])
        self.data = cv2.warpAffine(self.data, translation_matrix, (w, h))
        return self

    def crop(self, ):
        pass

    def rotate(self, angle):
        (h, w) = self.data.shape[:2]
        center = (int(w / 2), int(h / 2))
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
        self.data = cv2.warpAffine(self.data, rotation_matrix, (w, h))

    def save(self, filename: str = 'image.jpg'):
        cv2.imwrite(filename, self.data)
        return self

    def pixels(self):
        tp = ImageArray.Type
        self._array_ = ImageArray.convert.type(self.data, tp.CV2, tp.PIL)
        return self._array_.load()

    def from_pixels(self):
        tp = ImageArray.Type
        if self._array_ is not None:
            self.data = ImageArray.convert.type(self._array_, tp.PIL, tp.CV2)
            self._array_ = None

    def filter(self, mask, color=None, reverse: bool = False):
        from PyAsoka.Graphics.Mask import Mask
        if isinstance(mask, Mask):
            if color is None:
                if isinstance(self, Mask):
                    color = 0
                else:
                    color = (0, 0, 0)
            mask = cv2.inRange(mask(), 1, 255)
            if reverse:
                self.data[mask != 0] = color
            else:
                self.data[mask == 0] = color
        else:
            raise Exception('Передан неверный тип данных')
        return self

    def blur(self, x, y):
        self.data = cv2.blur(self.data, (1 + x * 2, 1 + y * 2))
        return self

    def gaussian_blur(self, x, y):
        self.data = cv2.GaussianBlur(self.data, (1 + x * 2, 1 + y * 2), 1)
        return self

    def toMask(self):
        from PyAsoka.Graphics.Mask import Mask
        return Mask(self.data)

    def toImage(self):
        from PyAsoka.Graphics.Image import Image
        return Image(self.data)

    @staticmethod
    def color_delta_difference(line1: numpy.ndarray, line2: numpy.ndarray):
        avg1 = numpy.sum(line1)
        avg2 = numpy.sum(line2)
        return int(avg2) - int(avg1)

    @staticmethod
    def unite(*args, vertical: bool = False):
        args = [arg.data for arg in args]
        if vertical:
            return ImageArray(numpy.vstack(args))
        else:
            return ImageArray(numpy.hstack(args))

    def find_border(self, point_s: Point, point_f: Point, thickness, sensitivity,
                    border_type: BorderType = BorderType.STRAIGHT, direction: Direction = None):
        if border_type == ImageArray.BorderType.STRAIGHT:
            angle = math.degrees(math.atan2(point_f.y - point_s.y, point_f.x - point_s.x))
            # print(angle)
            if angle == 0 or angle == 180 or angle == 90 or angle == 270:
                thickness = thickness // 2

                if angle == 180 or angle == 270:
                    point_s, point_f = point_f, point_s

                if angle == 0 or angle == 180:
                    if direction is None:
                        direction = ImageArray.Direction.TOP
                    y_from, y_to = point_s.y - thickness, point_f.y + thickness
                    line = ImageArray(self.data[y_from:y_to, point_s.x:point_f.x])
                    from_top = True if direction == direction.TOP else False
                    ind = find_border_horizontal(line, sensitivity, from_top)
                    return Point(point_s.x, point_s.y - thickness + ind), Point(point_f.x, point_f.y - thickness + ind)

                else:
                    if direction is None:
                        direction = ImageArray.Direction.LEFT
                    x_from, x_to = point_s.x - thickness, point_f.x + thickness
                    line = ImageArray(self.data[point_s.y:point_f.y, x_from:x_to])
                    line.data = numpy.rot90(line())
                    ind = find_border_horizontal(line, sensitivity, True if direction == direction.LEFT else False)
                    return Point(point_s.x + thickness - ind, point_s.y), Point(point_f.x + thickness - ind, point_f.y)


def find_border_horizontal(line, sensitivity, from_top=True):
    thickness = line().shape[0] // 2
    length = line().shape[1]
    splits = []
    differences = []
    delta = 0
    res, maybe = 0, 0
    min_avg = length * 3
    min_max_diff = length * 8
    # print(f'Поиск идет {"сверху" if from_top else "снизу"}. Критерии: средняя разница: {min_avg}, минимальное макс изменение: {min_max_diff}')

    for i in range(thickness * 2 - 1):
        ind = i if from_top else thickness * 2 - 1 - i

        sub_1 = line[ind, :]
        sub_2 = line[ind + 1 if from_top else ind - 1, :]
        split = ImageArray.color_delta_difference(sub_1, sub_2)
        splits.append(split)
        diff = sum(splits[i - 3: i] if i > 2 else splits[:i])
        differences.append(diff)
        delta += split
        arr = line.pixels()
        avg = sum(splits[i - 3: i]) // 3
        # print(f'{ind}: pix:{arr[50, ind]}, split: {split}, diff:{diff}, avgSplit:{avg}')
        # print(ind, split, diff, arr[100, ind], avg)
        if i > 3 and not res and min_max_diff < abs(diff):  # < 30000:
            if split > splits[i - 1]:
                maybe = ind
            else:
                res = ind - 1

    # print(f'Result: {res}\n')
    # line.show()
    return res
