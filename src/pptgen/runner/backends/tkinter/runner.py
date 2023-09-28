from pptgen import Group
from pptgen.runner.context import Context
import tkinter as tk
import tkinter.messagebox
import sys

class Backend:
    def __init__(self, context, width, height, scale, smart_refresh, validate_exit):
        self.context = context
        self.width = width
        self.height = height
        self.scale = scale
        self.smart_refresh = smart_refresh
        self.validate_exit = validate_exit
        self.continuous = False

        self.win = tk.Tk()
        self.can = tk.Canvas(self.win, width=width, height=height, bg="white")
        self.can.pack()
        self.can.bind("<ButtonPress-1>", self.click)
        self.can.bind("<ButtonPress-3>", self.clicks)
        self.can.bind("<ButtonRelease-3>", self.stop)

    def init(self):
        self.context.run_sequence(None)
        self.draw()

    def click(self, event):
        s = self.scale
        x, y = event.x/s, event.y/s
        if self.context.click(x, y) == Context.EXIT:
            self.exit(0)
        self.draw()

    def clicks(self, event):
        s = self.scale
        x, y = event.x/s, event.y/s
        self.continuous = True
        while self.continuous:
            status = self.context.click(x, y)
            if not self.smart_refresh or status == Context.REFRESH:
                self.draw()
            if status == Context.STOP:
                self.stop()
            elif status == Context.EXIT:
                self.exit(0)
            self.can.update()
        self.draw()
    
    def stop(self, event=None):
        self.continuous = False

    def exit(self, code):
        print(self.context.t)
        self.stop()
        if self.validate_exit:
            ok = tk.messagebox.askokcancel(title="tk_runner", message="Exit now?")
            if not ok:
                return
        sys.exit(code)

    def draw_group(self, shapes, group_x=0, group_y=0, group_alpha=1):
        s = self.scale
        for shape in shapes:
            alpha = shape.alpha*group_alpha
            if alpha == 0:
                continue
            if isinstance(shape, Group):
                self.draw_group(shape.shapes, shape.x-shape.ox, shape.y-shape.oy, alpha)
            else:
                x, y, cx, cy = shape.x+group_x, shape.y+group_y, shape.cx, shape.cy
                fill = "#"+shape.style.fill.color
                outline = "#"+shape.style.outline.color
                width = shape.style.width
                stipple = None if alpha == 1 else "gray50"
                self.can.create_rectangle(x*s, y*s, (x+cx)*s, (y+cy)*s, fill=fill, stipple=stipple, outline=outline, width=width*s)
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

def run(slide, width, height, scale, smart_refresh=False, validate_exit=False):
    context = Context(slide)
    backend = Backend(context, width, height, scale, smart_refresh, validate_exit)

    backend.init()

    backend.win.mainloop()
