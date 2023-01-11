import os.path

import cv2
import numpy
import PIL.Image as PImage

from PyAsoka.src.Graphics.ImageArray import ImageArray
from PyAsoka.src.Graphics.Geometry import Point
from copy import copy


class Image(ImageArray):
    def __init__(self, path: str = None, data=None, data_type: ImageArray.Type = None, data_scheme: ImageArray.Scheme = ImageArray.Scheme.BGR):
        super().__init__(data)
        self.scheme = None
        self._array_ = None

        if path is not None:
            self.from_file(path)
        elif data is not None:
            self.from_data(data, data_type, data_scheme)

    def from_file(self, path):
        if os.path.exists(path):
            self.data = cv2.imread(path)
            self.scheme = Image.Scheme.BGR
            return self
        else:
            raise Exception('Не найден файл изображения')

    def from_data(self, data, data_type: ImageArray.Type = None, data_scheme: ImageArray.Scheme = ImageArray.Scheme.BGR):
        if data_type is None:
            if isinstance(data, PImage.Image):
                data_type = Image.Type.PIL
            elif isinstance(data, numpy.ndarray):
                data_type = Image.Type.CV2

        if data_type == Image.Type.CV2:
            self.data = data
        elif data_type == Image.Type.PIL:
            self.data = Image.convert.type(data, Image.Type.PIL, Image.Type.CV2)
        self.scheme = data_scheme
        return self

    def __getitem__(self, item):
        return Image(data=super().__getitem__(item), data_scheme=self.scheme)

    def copy(self):
        data = copy(self.data)
        return Image(data=data, data_type=Image.Type.CV2, data_scheme=self.scheme)

    def show(self, win_name: str = 'Image', scheme: ImageArray.Scheme = None, stream: bool = False):
        # tp = Image.Scheme
        data = self.data
        #if scheme is not None and self.scheme != scheme:
        #    data = Image.convert.scheme(self.data, self.scheme, scheme)
        cv2.imshow(win_name, data)
        key = cv2.waitKey(1 if stream else 0)
        return key

    def __find_channel_data__(self, channel):
        if isinstance(channel, ImageArray.Channel):
            ch = Image.Channel
            sc = Image.Scheme
            channels = ch.channels()
            scheme = sc.RGB
            ind = 0
            for key in channels.keys():
                if channel in channels[key]:
                    scheme = key
                    for i in range(len(channels[key])):
                        if channels[key][i] == channel:
                            ind = i
            return scheme, ind
        else:
            raise Exception('Передан неверный тип данных')

    def getChannel(self, channel: ImageArray.Channel):
        from PyAsoka.src.Graphics.Mask import Mask
        scheme, ind = self.__find_channel_data__(channel)

        if self.scheme != scheme:
            data = Image.convert.scheme(self.data, self.scheme, scheme)
        else:
            data = copy(self.data)

        return Mask(cv2.split(data)[ind]) if scheme != Image.Scheme.GRAY else Mask(data)

    def setChannel(self, channel, ch_type: ImageArray.Channel = None):
        from PyAsoka.src.Graphics.Mask import Mask

        if isinstance(channel, Mask) and (ch_type is not None or channel.channel is not None):
            if ch_type is None and channel.channel is not None:
                ch_type = channel.channel
            channel = channel.data
        elif isinstance(channel, numpy.ndarray) and ch_type is not None:
            pass
        else:
            raise Exception('Передан неверный тип данных')

        if ch_type == Image.Channel.GRAY:
            raise Exception('Метод не поддерживается для одноканального типа изображений')

        scheme, ind = self.__find_channel_data__(ch_type)
        if self.scheme != scheme:
            data = Image.convert.scheme(self.data, self.scheme, scheme)
            channels = list(cv2.split(data))
            channels[ind] = channel
            data = cv2.merge(channels)
            self.data = Image.convert.scheme(data, scheme, self.scheme)
        else:
            channels = list(cv2.split(self.data))
            channels[ind] = channel
            self.data = cv2.merge(channels)
        return self

    def find_foreground(self, mask=None, scaling=3):
        from PyAsoka.src.Graphics.Mask import Mask

        image = self.data
        w, h = image.shape[:2]
        img = cv2.resize(image, (h // scaling, w // scaling))
        width, height = img.shape[:2]
        # show_image(image)

        if mask is None:
            mask = numpy.zeros(img.shape[:2], numpy.uint8)
            cv2.rectangle(mask, (0, 0), (height, width), cv2.GC_PR_BGD, -1)
        else:
            if isinstance(mask, Mask):
                mask = mask()
            elif isinstance(mask, numpy.ndarray):
                pass
            else:
                raise Exception('Передан неверный тип данных')

        rect = (1, 1, height - 1, width - 1)
        bgdModel1 = numpy.zeros((1, 65), numpy.float64)
        fgdModel1 = numpy.zeros((1, 65), numpy.float64)

        cv2.grabCut(img, mask, rect, bgdModel1, fgdModel1, 10, cv2.GC_INIT_WITH_RECT)
        cv2.grabCut(img, mask, rect, bgdModel1, fgdModel1, 10, cv2.GC_INIT_WITH_MASK)

        mask = numpy.where((mask == 1) + (mask == 3), 255, 0).astype('uint8')
        unique, counts = numpy.unique(mask, return_counts=True)
        mask = cv2.resize(mask, (h, w))
        cv2.bitwise_and(image, image, mask=mask)
        return Mask(mask)

    class Distortion:
        class Parameters:
            def __init__(self):
                self.matrix = None
                self.coefficients = None

        @staticmethod
        def adjust(image: ImageArray, params: Parameters):
            camera_matrix = params.matrix
            dist_coefs = params.coefficients
            
            rh, rw = image.data.shape[:2]
            img = image.data
            h, w = img.shape[:2]
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

            dst = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)
            dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

            # crop and save the image
            x, y, w, h = roi
            dst = dst[y:y+h, x:x+w]
            result = Image(data=cv2.cvtColor(dst, cv2.COLOR_RGB2BGR))
            h, w = dst.shape[:2]
            print(f'Resolution after undistort: ({w}x{h})')
            result.resize(rw, rh)
            return result

        @staticmethod
        def calibrate(images):
            CHECKERBOARD = (9, 6)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            objpoints = []
            imgpoints = []

            # Определение мировых координат для 3D точек
            objp = numpy.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), numpy.float32)
            objp[0, :, :2] = numpy.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
            prev_img_shape = None
            params = Image.Distortion.Parameters()

            for i in range(len(images)):
                img = images[i].data
                h, w = img.shape[:2]
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Найти углы шахматной доски
                # Если на изображении найдено нужное количество углов, тогда ret = true
                ret, corners = cv2.findChessboardCorners(img, CHECKERBOARD)

                if ret is True:
                    print(f'Chessboard found at {i + 1} image')
                    objpoints.append(objp)
                    # уточнение координат пикселей для заданных 2d точек.
                    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

                    imgpoints.append(corners2)
                    # Нарисовать и отобразить углы
                    img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)

                else:
                    print(f'Warning! Chessboard not found at {i + 1} image')

            if len(objpoints) and len(imgpoints):
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
                params.matrix = mtx
                params.coefficients = dist
                return params
            else:
                print("No matching images. Can't calculate distortion coefficients")
                return False

    def find_contour_linear(self, point1: Point, point2: Point, thickness, smoothing, sensitivity,
                            channels: list = (ImageArray.Channel.RED, ImageArray.Channel.GREEN, ImageArray.Channel.BLUE),
                            direction: ImageArray.Direction = ImageArray.Direction.LEFT, diapason: tuple = (0, 1),
                            approximation=False):
        from PyAsoka.src.Geometry.Point import Point
        from PyAsoka.src.Geometry.Vector import Vector
        from PyAsoka.src.Geometry.Straight import Straight
        from PyAsoka.src.Geometry.Geometry import Geometry

        point1 = point1.toAPoint()
        point2 = point2.toAPoint()
        vector = Vector(point1, point2)
        length = round(vector.length() * (diapason[1] - diapason[0]))
        indent = round(vector.length() * diapason[0])
        vector = vector.unit()
        perpend = vector.copy().rotate(90)

        masks = [self.getChannel(channel) for channel in channels]
        contours = [[None for i in range(length)] for i in range(len(masks))]
        if isinstance(sensitivity, int):
            sensitivity = [sensitivity for i in range(len(masks))]

        for m in range(len(masks)):
            pixels = masks[m].pixels()
            img = masks[m].copy()
            for i in range(length):
                points = []
                base_point = Point(point1.x + vector.x * (i + indent), point1.y + vector.y * (i + indent))
                rng = range(-thickness // 2, thickness // 2, 1) if direction == Image.Direction.LEFT else range(thickness // 2, -thickness // 2, -1)
                for j in rng:
                    points.append(Point(round(base_point.x + perpend.x * j), round(base_point.y + perpend.y * j)))

                for j in range(smoothing, len(points) - smoothing - 1, 1):
                    # points[j].draw(img, size=2)
                    delta = abs(pixels[points[j].x, points[j].y] - pixels[points[j - smoothing].x, points[j - smoothing].y])
                    # print(f'Pixel: {pixels[points[j].x, points[j].y]}, Delta: {delta}')
                    if delta > sensitivity[m]:
                        ind, max_ind = j, 0
                        for k in range(smoothing - 1):
                            dlt = abs(pixels[points[j - k].x, points[j - k].y] - pixels[points[j - k - 1].x, points[j - k - 1].y])
                            if dlt > max_ind:
                                max_ind = dlt
                                ind = j - k - 1
                        point = points[ind]
                        img.data[point.y, point.x] = 255
                        # point.draw(img, color=(255, 0, 0), size=1)
                        contours[m][i] = point
                        break
                # print('\n-------------')
            # img.copy().resize(scale=0.5).show()

        img = self.copy()
        avg_contour = [None for i in range(length)]
        contour = [None for i in range(length)]
        for i in range(length):
            point = Point.average([cont[i] for cont in contours])
            if point is not None:
                point.draw(img, size=1)
            avg_contour[i] = point

        # img.copy().resize(scale=0.5).show()
        contour = copy(avg_contour)

        if approximation:
            return Geometry.linearApproximation2D(contour)
        else:
            sections_count = round(length / 50)
            sections_avg = []
            sections_vect = []
            step = length // sections_count
            for i in range(sections_count):
                average = Point.average(contour[step * i: step * (i + 1)])
                if average is not None:
                    sections_avg.append(average)
                    sections_avg[i].draw(img, color=(255, 0, 0), size=3)

            OX_vect = Vector(Point(0, 0), Point(1, 0))
            angles = []
            for i in range(len(sections_avg) - 1):
                vector = Vector(sections_avg[i].toAPoint(), sections_avg[i + 1].toAPoint())
                angle = OX_vect.angle(vector)
                sections_vect.append(vector)
                angles.append(angle)
                # print(angle)
            point = Point.average(contour)
            angle = sum(angles) / len(angles)
            vector = OX_vect.copy().rotate(angle)

            print(f'Point: {point}, Angle: {angle}')
            # img.copy().resize(scale=0.7).show()

            img = self.copy()
            point1 = Point(round(point.x + vector.x * length / 2), round(point.y + vector.y * length / 2))
            point2 = Point(round(point.x - vector.x * length / 2), round(point.y - vector.y * length / 2))
            cv2.line(img(), point1.arr(), point2.arr(), (0, 0, 255), 2)
            # img.copy().resize(scale=0.7).show()

            return Straight(point.toAPoint(), vector)

    def toBGR(self):
        scheme = Image.Scheme
        if self.scheme != scheme.BGR:
            Image.convert.scheme(self, self.scheme, scheme.BGR)
        return self

    def toRGB(self):
        scheme = Image.Scheme
        if self.scheme != scheme.RGB:
            Image.convert.scheme(self, self.scheme, scheme.RGB)
        return self

    def toHSV(self):
        scheme = Image.Scheme
        if self.scheme != scheme.HSV:
            Image.convert.scheme(self, self.scheme, scheme.HSV)
        return self

