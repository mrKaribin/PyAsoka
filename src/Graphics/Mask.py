from copy import copy
from PyAsoka.src.Graphics.ImageArray import ImageArray

from skimage.metrics import structural_similarity

import cv2
import numpy


class Mask(ImageArray):
    def __init__(self, data=None, channel: ImageArray.Channel = None):
        super().__init__(data)
        self.data = data
        self.channel = channel

    def createZeros(self, w, h):
        self.data = numpy.zeros((h, w), numpy.uint8)
        return self

    def __getitem__(self, item):
        return Mask(data=super().__getitem__(item), channel=self.channel)

    def __and__(self, other):
        if isinstance(other, Mask):
            return Mask(self.data & other.data)
        elif isinstance(other, numpy.ndarray):
            return Mask(self.data & other)
        else:
            raise Exception('Передан неверный тип данных')

    def __or__(self, other):
        if isinstance(other, Mask):
            return Mask(self.data | other.data)
        elif isinstance(other, numpy.ndarray):
            return Mask(self.data | other)
        else:
            raise Exception('Передан неверный тип данных')

    def __xor__(self, other):
        if isinstance(other, Mask):
            return Mask(self.data ^ other.data)
        elif isinstance(other, numpy.ndarray):
            return Mask(self.data ^ other)
        else:
            raise Exception('Передан неверный тип данных')

    def similarityWith(self, mask: 'Mask'):
        return structural_similarity(self(), mask(), full=True)

    def copy(self):
        data = copy(self.data)
        return Mask(data=data, channel=self.channel)

    def range(self, lower: int = 0, upper: int = 255):
        return Mask(cv2.inRange(self.data, lower, upper))

    def average(self, iters=5, blur=5, threshold=50):
        for k in range(iters):
            self.gaussian_blur(blur, blur)
            mask = self.range(lower=threshold)
            self.data[mask == 0] = 0
        return self

    def color_fragmentation(self, count, max_col: int = 255, min_col: int = 0):
        step = (max_col - min_col) // count
        new_step = 255 // count
        for j in range(count):
            level = max_col - step * j
            color = 255 - new_step * j
            mask = self.range(level - step, level)
            self.filter(mask, color, True)
