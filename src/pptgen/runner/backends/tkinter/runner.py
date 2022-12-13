from pptgen import Group
from pptgen.runner.context import Context
import tkinter as tk
import sys

class Backend:
    def __init__(self, context, width, height, scale):
        self.context = context
        self.width = width
        self.height = height
        self.scale = scale
        self.continuous = False

        self.win = tk.Tk()
        self.can = tk.Canvas(self.win, width=width, height=height, bg="white")
        self.can.pack()
        self.can.bind("<ButtonPress-1>", self.click)
        self.can.bind("<ButtonPress-3>", self.clicks)
        self.can.bind("<ButtonRelease-3>", self.stop)

    def init(self):
        self.context.run_sequence("main", self)

    def click(self, event):
        s = self.scale
        x, y = event.x/s, event.y/s
        if self.context.click(x, y, self):
            sys.exit()

    def clicks(self, event):
        s = self.scale
        x, y = event.x/s, event.y/s
        self.continuous = True
        while self.continuous:
            if self.context.click(x, y, self):
                sys.exit()
            self.can.update()
    
    def stop(self, event):
        self.continuous = False

    def draw_group(self, shapes):
        s = self.scale
        for shape in shapes:
            if isinstance(shape, Group):
                self.draw_group(shape.shapes)
            else:
                x, y, cx, cy = shape.x, shape.y, shape.cx, shape.cy
                fill = "#"+shape.style.fill.color
                outline = "#"+shape.style.outline.color
                width = shape.style.width
                self.can.create_rectangle(x*s, y*s, (x+cx)*s, (y+cy)*s, fill=fill, outline=outline, width=width)
                if shape.text.content is not None:
                    fill = "#"+shape.text.color.color
                    text = shape.text.content
                    size = shape.text.size
                    self.can.create_text((x+cx/2)*s, (y+cy/2)*s, fill=fill, text=text, font=f"Arial {size//100}")

    def clear(self):
        self.can.delete(tk.ALL)

    def draw(self):
        self.clear()
        self.draw_group((shape for shape in self.context.visible if shape.visible))

def run(slide, width, height, scale):
    context = Context(slide)
    backend = Backend(context, width, height, scale)

    backend.init()

    backend.win.mainloop()