from PyAsoka.src.Graphics.Image import Image


class ImageAnalyzer:

    class RGB:
        def __init__(self, image: Image):
            self.image = image.copy().toRGB()
            self.red = image.getChannel(Image.Channel.RED)
            self.green = image.getChannel(Image.Channel.GREEN)
            self.blue = image.getChannel(Image.Channel.BLUE)

    class HSV:
        def __init__(self, image: Image):
            self.image = image.copy().toHSV()
            self.hue = image.getChannel(Image.Channel.HUE)
            self.saturation = image.getChannel(Image.Channel.SATURATION)
            self.value = image.getChannel(Image.Channel.VALUE)

    class LAB:
        def __init__(self, image: Image):
            self.image = image.copy()
            self.l = image.getChannel(Image.Channel.LAB_L)
            self.a = image.getChannel(Image.Channel.LAB_A)
            self.b = image.getChannel(Image.Channel.LAB_B)

    def __init__(self, image: Image = None):
        if image is not None:
            self.update(image)

    def update(self, image):
        self.original = image.copy().toBGR()
        self.rgb = ImageAnalyzer.RGB(image)
        self.hsv = ImageAnalyzer.HSV(image)
        self.lab = ImageAnalyzer.LAB(image)

    def collage(self):
        rgb = Image.unite(self.rgb.red, self.rgb.green, self.rgb.blue)
        hsv = Image.unite(self.hsv.hue, self.hsv.saturation, self.hsv.value)
        lab = Image.unite(self.lab.l, self.lab.a, self.lab.b)
        return Image.unite(rgb, hsv, lab, vertical=True).toMask()
