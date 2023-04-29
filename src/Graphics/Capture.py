import os

from PyAsoka.src.Graphics.Image import *

import pytube


def retry_access_ty_object(url, max_retries=100, interval_secs=3, on_progress_callback=None):
    from time import sleep
    last_exception = None
    for i in range(max_retries):
        try:
            yt = pytube.YouTube(url, on_progress_callback=on_progress_callback)
            title = yt.title  # Access the title of the YouTube object.
            return yt  # Return the YouTube object if successful.
        except Exception as err:
            last_exception = err  # Keep track of the last exception raised.
            print(f"Failed to create YouTube object or access title. Retrying... ({i + 1}/{max_retries})")
            sleep(interval_secs)  # Wait for the specified interval before retrying.


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

    @property
    def width(self):
        return round(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return round(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def fps(self):
        return round(self.capture.get(cv2.CAP_PROP_FPS))

    def isOpened(self):
        return self.capture.isOpened()

    def setPosition(self, pos: int):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, pos)

    def read(self):
        ok, frame = self.capture.read()
        if ok:
            return Image(data=frame)
        else:
            return False

    def release(self):
        self.capture.release()

    @staticmethod
    def loadCycledVideoFromYoutube(url, duration, resolution):
        from os import path, remove
        from subprocess import check_call

        demo_name = 'demo.mp4'
        cycled_name = 'cycled.mp4'
        if path.exists(demo_name):
            remove(demo_name)
        if path.exists(cycled_name):
            remove(cycled_name)

        fr, to = '00:00:00.00', f'00:00:{duration:02}.00'
        video = retry_access_ty_object(url)
        print(video.title)
        for streams in video.streams:
            print(streams)
        stream = video.streams.filter(res=f'{resolution}p').first()  #.download(filename='fireplace_full.webm')
        # exit()

        print(f'Using stream: itag={stream.itag} type={stream.type}')
        process_call_str = f'ffmpeg -ss {fr} -to {to} -i "{stream.url}" ' \
                           f'-acodec aac -b:a 192k -avoid_negative_ts make_zero "{demo_name}"'

        status = check_call(process_call_str, shell=True)
        print('Downloaded:', status)

        capture = Capture(demo_name)
        if capture.isOpened() == False:
            print('Ошибка открытия файла')
            exit()

        count = 0
        frag_count = 0
        start_ind = 0
        end_ind = 0
        pat_frame = None
        fps = capture.fps
        res = (capture.width, capture.height)
        print(f'Частота кадров: {fps}')
        print(f'Разрешение: {capture.width} x {capture.height}')

        while (frame := capture.read()) is not False:
            try:
                frame.resize(scale=0.3)
                # frame.show(stream=True)
                count += 1
                frag_count += 1
                if count % fps == 0 and (count / fps) % 10 == 0:
                    print(f'Recd {count / fps} seconds')

                if count == 10:
                    pat_frame = frame
                    continue
                if pat_frame is not None:
                    (score, diff) = pat_frame.getChannel(Image.Channel.GRAY).similarityWith(
                        frame.getChannel(Image.Channel.GRAY))

                    if score > 0.98:
                        end_ind = count
                        print(f'Fragment {frag_count} frames long detected in ({start_ind} - {end_ind}) frames')
                        capture.release()
                        break

                    if score > 0.89:
                        print(count, score)
                        pat_frame = frame
                        frag_count = 0
                        start_ind = count
                        # input()

            except Exception as e:
                print('Exception:', e)
                break

        if end_ind == 0:
            end_ind = count
        capture.release()

        capture = Capture(demo_name)
        output = cv2.VideoWriter(cycled_name, cv2.VideoWriter_fourcc(*'MP4V'), fps, res)
        print('Writing fragment...')

        count = 0
        wrote = 0
        percent = 0
        while (frame := capture.read()) is not False:
            count += 1
            if start_ind <= count <= end_ind:
                output.write(frame())
                wrote += 1
                prc = int(100 / (end_ind - start_ind) * wrote)
                if prc > percent:
                    print(f'writing {prc}%')
                    percent = prc
            if count > end_ind:
                break

        capture.release()
        output.release()
