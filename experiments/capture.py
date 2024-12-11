from PIL import Image
from io import BytesIO

class Recorder:
    def __init__(self):
        self.frames = []

    def save_frame(self, canvas):
        postscript = canvas.postscript()
        stream = BytesIO(postscript.encode())
        img = Image.open(stream)
        self.frames.append(img)

    def save_video(self, name):
        if len(self.frames) < 3:
            return
        _, img, *imgs = self.frames
        img.save(fp=f"{name}.gif", format='GIF', append_images=imgs, save_all=True, optimize=True, duration=20, loop=0)
