import multiprocessing
import os

import cv2

from PyAsoka.Graphics.Image import *


class CaptureProperties:
    def __init__(self, load: bool = False,
                 width: int = None, height: int = None, fps: int = 30,
                 brightness: int = None, contrast: int = None,
                 saturation: int = None, hue: int = None, gamma: int = None,
                 temperature: int = None, sharpness: int = None, focus: int = None):
        self.width = width
        self.height = height
        self.fps = fps
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.hue = hue
        self.gamma = gamma
        self.temperature = temperature
        self.sharpness = sharpness
        self.focus = focus


class Capture:
    def __init__(self, arg, properties: CaptureProperties = CaptureProperties()):
        self.capture = None
        self.frames = None
        self.properties = properties

        if isinstance(arg, str):
            self.from_file(arg)
        elif isinstance(arg, int):
            self.from_camera(arg)

        self.set_properties(properties)

    def set_properties(self, properties: CaptureProperties):
        if properties.fps is not None:
            self.capture.set(cv2.CAP_PROP_FPS, properties.fps)
        if properties.width is not None:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, properties.width)
        if properties.height is not None:
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, properties.height)
        if properties.brightness is not None:
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, properties.brightness)
        if properties.contrast is not None:
            self.capture.set(cv2.CAP_PROP_CONTRAST, properties.contrast)
        if properties.saturation is not None:
            self.capture.set(cv2.CAP_PROP_SATURATION, properties.saturation)
        if properties.hue is not None:
            self.capture.set(cv2.CAP_PROP_HUE, properties.hue)
        if properties.gamma is not None:
            self.capture.set(cv2.CAP_PROP_GAMMA, properties.gamma)
        if properties.temperature is not None:
            self.capture.set(cv2.CAP_PROP_TEMPERATURE, properties.temperature)
        if properties.sharpness is not None:
            self.capture.set(cv2.CAP_PROP_SHARPNESS, properties.sharpness)
        if properties.focus is not None:
            self.capture.set(cv2.CAP_PROP_FOCUS, properties.focus)

    def from_file(self, path):
        if os.path.exists(path):
            self.capture = cv2.VideoCapture(path)
            self.frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        else:
            raise Exception('Не найден файл для чтения')

    def from_camera(self, cam_id):
        self.capture = cv2.VideoCapture(cam_id)
        self.frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def isOpened(self):
        return self.capture.isOpened()

    def read(self):
        ok, frame = self.capture.read()
        if ok:
            return Image(data=frame)
        else:
            return False

    def release(self):
        self.capture.release()
