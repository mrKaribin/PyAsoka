import cv2
import math
import mediapipe as mp

from enum import Enum, auto
from PyAsoka.Maths.Geometry.APoint import APoint as Point
from PyAsoka.Connections.Signal import Signal
from PySide6.QtCore import QObject


class Finger:
    class State(Enum):
        STRAIGHT = auto()
        BENDED = auto()
        COMPRESSED = auto()
        UNDEFINED = auto()

    def __init__(self):
        self.visible = False
        self.state = Finger.State.UNDEFINED
        self.points = []
        self.tip = None
        self.falange1 = None
        self.falange2 = None
        self.base = None

        self.base_angle = 0
        self.falange1_angle = 0
        self.falange2_angle = 0

    def update(self, base, point1, point2, point3, point4):
        self.points = [point1, point2, point3, point4]
        self.tip = point4
        self.falange1 = point3
        self.falange2 = point2
        self.base = point1

        self.base_angle = self.__angle__(base, point1, point2)
        self.falange2_angle = self.__angle__(point1, point2, point3)
        self.falange1_angle = self.__angle__(point2, point3, point4)

        self.check_status()

    @staticmethod
    def __angle__(point1, point2, point3):
        from PyAsoka.Maths.Geometry.AVector import AVector
        point1 = Point(point1.x, point1.y, point1.z)
        point2 = Point(point2.x, point2.y, point2.z)
        point3 = Point(point3.x, point3.y, point3.z)
        vec1 = AVector(point2, point1)
        vec2 = AVector(point2, point3)
        if (l1 := vec1.length()) != 0 and (l2 := vec2.length()) != 0:
            return math.degrees(math.acos((vec1 ** vec2) / (l1 * l2)))
        else:
            return 180

    @staticmethod
    def __distance__(point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2 + (point1.z - point2.z) ** 2)

    def __is_semi_line__(self, point1, point2, point3, coef):
        s_point = Point((point1.x + point3.x) / 2, (point1.y + point3.y) / 2, (point1.z + point3.z) / 2)
        dist = self.__distance__(point1, point3)
        fault = self.__distance__(s_point, point2)
        return fault < dist * coef

    def check_status(self):
        if len(self.points) > 0:
            for point in self.points:
                if point.x < 0 or point.x > 1 or point.y < 0 or point.y > 1:
                    self.visible = False
                    self.state = self.State.UNDEFINED
                    return

            self.visible = True
            if self.base_angle < 150:
                if self.falange1_angle < 150:
                    self.state = self.State.COMPRESSED
                else:
                    self.state = self.State.BENDED
            else:
                self.state = self.State.STRAIGHT
        else:
            self.visible = False
            self.state = Finger.State.UNDEFINED

    def clean(self):
        self.visible = False
        self.state = Finger.State.UNDEFINED
        self.points = []
        self.tip = None
        self.falange1 = None
        self.falange2 = None
        self.base = None


class FirstFinger(Finger):
    def check_status(self):
        if len(self.points) > 0:
            for point in self.points:
                if point.x < 0 or point.x > 1 or point.y < 0 or point.y > 1:
                    self.visible = False
                    self.state = self.State.UNDEFINED
                    return

            self.visible = True
            if self.falange1_angle < 150:
                self.state = self.State.COMPRESSED
            else:
                self.state = self.State.STRAIGHT
        else:
            self.visible = False
            self.state = Finger.State.UNDEFINED


class HandData:
    def __init__(self, _landmarks=None):
        self.landmarks = None
        self.points = range(21)
        if _landmarks is not None:
            self.update(_landmarks)

    def update(self, _landmarks):
        self.landmarks = _landmarks
        self.points = []
        for idx, landmark in enumerate(self.landmarks.landmark):
            # print(f'{idx}: ({landmark.x:.2}, {landmark.y:.2}, {landmark.z:.2}')
            self.points.insert(idx, landmark)


class Hand(QObject, HandData):
    mpHands = mp.solutions.hands
    mpDraw = mp.solutions.drawing_utils
    detector = mpHands.Hands()
    # moved = QSignal([float, float])

    class State(Enum):
        UNDEFINED = auto()
        CURSOR = auto()
        PRESSED = auto()
        SCROLL = auto()
        PALM = auto()
        ROCK = auto()

    def __init__(self):
        super().__init__()
        self.buffer = []
        self.visible = False
        self.state = Hand.State.UNDEFINED
        self.base = None
        self.angle = 0
        self.z_angle = 0
        self.finger1 = FirstFinger()
        self.finger2 = Finger()
        self.finger3 = Finger()
        self.finger4 = Finger()
        self.finger5 = Finger()
        self.fingers = [self.finger1, self.finger2, self.finger3, self.finger4, self.finger5]

        self.pressed_count = 0
        self.cursor_updated = False
        self.cursor_delta = None
        self.last_cursor_position = None

        self.moved = Signal(float, float)
        self.scrolled = Signal(float, float)
        self.clicked = Signal(Point)
        self.pressed = Signal(Point)
        self.released = Signal(Point)

    def update(self, hand: HandData):
        landmarks = hand.landmarks
        self.buffer.append(landmarks)
        if len(self.buffer) > 3:
            self.buffer.remove(self.buffer[0])
        d_landmarks = [Point(0, 0) for i in range(21)]
        for data in self.buffer:
            for idx, landmark in enumerate(data.landmark):
                d_landmarks[idx].x += landmark.x
                d_landmarks[idx].y += landmark.y

        self.landmarks = landmarks
        self.points = []
        maximum = 0.02
        for idx, landmark in enumerate(landmarks.landmark):
            landmark.x = d_landmarks[idx].x / len(self.buffer)
            landmark.y = d_landmarks[idx].y / len(self.buffer)
            self.points.insert(idx, landmark)

        self.base = self.points[0]
        self.finger1.update(self.base, *self.points[1:5])
        self.finger2.update(self.base, *self.points[5:9])
        self.finger3.update(self.base, *self.points[9:13])
        self.finger4.update(self.base, *self.points[13:17])
        self.finger5.update(self.base, *self.points[17:])
        self.update_angles()
        self.update_status()

        # print(f'x-angle: {self.angle}, z-angle: {self.z_angle}')

    def update_angles(self):
        k = Point(-self.finger3.base.x + self.base.x, self.finger3.base.y - self.base.y)
        l = Point(1, 0)
        angle = (k.x * l.x + k.y * l.y) / (math.sqrt(k.x ** 2 + k.y ** 2) * math.sqrt(l.x ** 2 + l.y ** 2))
        if self.base.y > self.finger3.base.y:
            self.angle = int(math.acos(angle) / math.pi * 180)
        else:
            self.angle = 360 - int(math.acos(angle) / math.pi * 180)

        from PyAsoka.Maths.Geometry.AVector import AVector
        point1 = Point(self.finger5.base.x, self.finger5.base.y, self.finger5.base.z)
        point2 = Point(self.finger2.base.x, self.finger2.base.y, self.finger2.base.z)
        vec1 = AVector(point1, point2)
        vec2 = AVector(0, 0, 1)
        if (l1 := vec1.length()) != 0 and (l2 := vec2.length()) != 0:
            self.z_angle = math.degrees(math.acos((vec1 ** vec2) / (l1 * l2)))
        else:
            self.z_angle = 0

    def update_cursor_position(self):
        current_pos = self.finger3.base
        if self.last_cursor_position is not None:
            self.cursor_delta = Point(current_pos.x - self.last_cursor_position.x, current_pos.y - self.last_cursor_position.y)
            if self.cursor_delta.x == 0 and self.cursor_delta.y == 0:
                self.cursor_delta = None
        self.last_cursor_position = current_pos
        self.cursor_updated = True

    def update_status(self):
        last_state = self.state
        self.state = self.State.UNDEFINED
        self.cursor_updated = False
        st = Finger.State
        dist_1_2 = Finger.__distance__(self.finger1.tip, self.finger2.tip)
        # print(f"Dist: {dist_1_2}")

        if 50 < self.angle < 130 and 90 < self.z_angle < 120:

            if last_state != self.State.PRESSED and \
                    self.finger1.state == st.STRAIGHT and \
                    self.finger2.state == st.STRAIGHT and \
                    self.finger3.state == st.COMPRESSED and \
                    self.finger4.state == st.COMPRESSED and \
                    self.finger5.state == st.COMPRESSED:
                self.state = Hand.State.CURSOR
                self.update_cursor_position()
                if self.cursor_delta is not None:
                    self.moved(self.cursor_delta.x, self.cursor_delta.y)

            if dist_1_2 < 0.08 and \
                    self.finger3.state == st.COMPRESSED and \
                    self.finger4.state == st.COMPRESSED and \
                    self.finger5.state == st.COMPRESSED:
                self.state = Hand.State.PRESSED
                self.pressed_count += 1
                if self.last_cursor_position is None:
                    self.last_cursor_position = self.finger3.base
                self.cursor_updated = True
                if self.pressed_count >= 10 and self.last_cursor_position is not None:  # +79117120956
                    self.pressed(self.last_cursor_position)
                    self.update_cursor_position()
                    if self.cursor_delta is not None:
                        self.moved(self.cursor_delta.x, self.cursor_delta.y)

            else:
                if 0 < self.pressed_count < 10 and self.last_cursor_position is not None:
                    self.clicked(self.last_cursor_position)
                elif self.pressed_count >= 10:
                    self.released(self.last_cursor_position)
                self.pressed_count = 0

            if self.finger2.state == st.STRAIGHT and \
                    self.finger3.state == st.STRAIGHT and \
                    self.finger4.state in [st.COMPRESSED, st.BENDED] and \
                    self.finger5.state in [st.COMPRESSED, st.BENDED]:
                self.state = Hand.State.SCROLL
                self.update_cursor_position()
                if self.cursor_delta is not None:
                    self.scrolled(self.cursor_delta.x, self.cursor_delta.y)

            if self.finger1.state == st.STRAIGHT and \
                    self.finger2.state == st.COMPRESSED and \
                    self.finger3.state == st.COMPRESSED and \
                    self.finger4.state == st.COMPRESSED and \
                    self.finger5.state == st.STRAIGHT:
                self.state = Hand.State.ROCK

            if not self.cursor_updated:
                self.last_cursor_position = None

        else:
            self.clean_status()

    def clean_status(self):
        self.state = Hand.State.UNDEFINED
        self.last_cursor_position = None
        self.pressed_count = 0

    def clean(self):
        self.landmarks = None
        self.points = range(21)
        self.visible = False
        self.state = Hand.State.UNDEFINED
        self.base = None
        self.angle = 0
        self.finger1.clean()
        self.finger2.clean()
        self.finger3.clean()
        self.finger4.clean()
        self.finger5.clean()

        self.pressed_count = 0
        self.last_cursor_position = None

    def draw(self, image):
        self.mpDraw.draw_landmarks(image, self.landmarks, self.mpHands.HAND_CONNECTIONS)
        for finger in self.fingers:
            tip = finger.tip
            h, w = image.shape[:2]
            cx, cy = int(tip.x * w), int(tip.y * h)
            cv2.circle(image, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

    @staticmethod
    def detect(image):
        hands_data = Hand.detector.process(image)
        if hands_data.multi_hand_landmarks:
            return [HandData(landmarks) for landmarks in hands_data.multi_hand_landmarks]
        else:
            return None

