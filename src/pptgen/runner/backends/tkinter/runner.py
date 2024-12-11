from pptgen import Group
from pptgen.runner.context import Context
import tkinter as tk
import tkinter.messagebox
import tkinter.font
import sys

class Backend:
    def __init__(self, context, width, height, scale, smart_refresh, validate_exit, show_sequence, show_debug, frame_callback):
        self.context = context
        self.width = width
        self.height = height
        self.scale = scale
        self.smart_refresh = smart_refresh
        self.validate_exit = validate_exit
        self.show_sequence = show_sequence
        self.show_debug = show_debug
        self.frame_callback = frame_callback
        self.continuous = False

        self.debugs = [shape for shape in context.visible if hasattr(shape, "debug")]
        print(len(self.debugs))

        self.win = tk.Tk()
        self.can = tk.Canvas(self.win, width=width, height=height, bg="white")
        self.can.grid(row=0, column=0)
        self.can.bind("<ButtonPress-1>", self.click)
        self.can.bind("<ButtonPress-3>", self.clicks)
        self.can.bind("<ButtonRelease-3>", self.stop)

        if show_sequence:
            self.can.bind("<ButtonPress-2>", self.update_animations)

            family = tk.font.nametofont("TkFixedFont").actual()["family"]
            mono = tk.font.Font(family=family, size=10)
            self.animations = tk.Listbox(self.win, font=mono)
            self.animations.grid(row=0, column=2, sticky=tk.N+tk.S)

            self.scrollbar = tk.Scrollbar(self.win)
            self.scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
            self.scrollbar.config(command = self.animations.yview)
            self.animations.config(yscrollcommand = self.scrollbar.set)

    def init(self):
        self.context.run_sequence(None)
        self.draw()

    def update_animations(self, event):
        if not self.show_sequence:
            return
        s = self.scale
        x, y = event.x/s, event.y/s
        target = self.context.get_under(x, y)
        if target is None or target.id not in self.context.sequences:
            id = "main"
        else:
            id = target.id
        sequence = self.context.sequences.get(id)
        head = self.context.sequences_head.get(id)
        self.animations.delete(0, tk.END)
        self.animations.insert(tk.END, *[
            (">" if i == head else " ") +
            ("+" if animation.click else " ") +
            animation.__class__.__name__ +
            ("(self)" if animation.target == id else "")
            for i, animation in enumerate(sequence)])

    def click(self, event):
        self.update_animations(event)
        s = self.scale
        x, y = event.x/s, event.y/s
        if self.context.click(x, y) == Context.EXIT:
            if self.exit():
                return
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
                if self.exit():
                    return
            self.can.update()
        self.draw()
    
    def stop(self, event=None):
        self.continuous = False

    def exit(self):
        print(self.context.t)
        self.stop()
        if self.validate_exit:
            ok = tk.messagebox.askokcancel(title="tk_runner", message="Exit now?")
            if not ok:
                return False
        self.win.destroy()
        return True

    def draw_shape(self, shape, group_x=0, group_y=0, alpha=1):
        s = self.scale
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

    def draw_group(self, shapes, group_x=0, group_y=0, group_alpha=1):
        for shape in shapes:
            alpha = shape.alpha*group_alpha
            if alpha == 0:
                continue
            if isinstance(shape, Group):
                self.draw_group(shape.shapes, shape.x-shape.ox, shape.y-shape.oy, alpha)
            else:
                self.draw_shape(shape, group_x, group_y, alpha)
        if self.show_debug and not self.continuous:
            for shape in self.debugs:
                debug = shape.debug()
                if debug is not None:
                    self.draw_shape(debug)

    def clear(self):
        self.can.delete(tk.ALL)

    def draw(self):
        self.clear()
        self.draw_group((shape for shape in self.context.visible if shape.visible))
        if self.frame_callback is not None:
            self.frame_callback(self)

def run(slide, width, height, scale, smart_refresh=False, validate_exit=False, show_sequence=False, show_debug=False, frame_callback=None):
    context = Context(slide)
    backend = Backend(context, width, height, scale, smart_refresh, validate_exit, show_sequence, show_debug, frame_callback)

    backend.init()

    backend.win.mainloop()
