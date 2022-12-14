from pptgen import Document, Group
from pptgen.animation import *
import sys

print = lambda *arg, **kwargs: None

class Context:
    CONTINUE = 0
    REFRESH = 1
    STOP = 2
    EXIT = 3
    def __init__(self, slide):
        self.slide = slide
        self.shapes = {shape.id:shape for shape in slide.shapes}
        self.timeline = slide.timeline
        self.sequences = slide.timeline.contexts
        self.sequences_head = {k:0 for k in slide.timeline.contexts.keys()}
        self.visible = list(reversed(sorted(slide.shapes, key=lambda shape:shape.z)))

        def rec_alpha(shapes):
            for shape in shapes:
                if isinstance(shape, Group):
                    shape.alpha = 1
                    rec_alpha(shape.shapes)
                else:
                    shape.alpha = 1-(shape.style.fill.alpha/1000)

        rec_alpha(slide.shapes)
        for shape in slide.shapes:
            if isinstance(shape, Group):
                shape.x = shape.get_x()
                shape.y = shape.get_y()
            shape.ox = shape.x
            shape.oy = shape.y
            shape.visible = True

        must_be = {}
        for context in slide.timeline.contexts.values():
            for animation in context:
                id = animation.target
                if id not in must_be:
                    visible = animation.preset != Animation.ENTR
                    must_be[id] = visible
                    self.shapes[id].visible = visible

    def apply(self, animation):
        print(animation.target)
        shape = self.shapes[animation.target]
        if animation.preset == Animation.ENTR:
            shape.visible = True
        elif animation.preset == Animation.EXIT and animation.repeat == 1000:
            shape.visible = False

        if isinstance(animation, Appear):
            print("Appear")
        if isinstance(animation, Disappear):
            print("Disappear")
        if isinstance(animation, FadeIn):
            print("FadeIn")
            shape.alpha = animation.repeat/1000
        if isinstance(animation, FadeOut):
            print("FadeOut")
            if animation.repeat == 1000:
                print("UNSUPPORTED")
                sys.exit(1)
            shape.alpha = 1-animation.repeat/1000
        if isinstance(animation, SlideIn):
            print("SlideIn")
            shape.x = shape.ox
            shape.y = shape.oy
        if isinstance(animation, SlideOut):
            print("SlideOut")
            if animation.repeat > 10:
                print("UNSUPPORTED")
                sys.exit(1)
            if hasattr(animation, "ox"):
                shape.x = animation.ox
                shape.y = animation.oy
            else:
                animation.ox = shape.x
                animation.oy = shape.y
        if isinstance(animation, Path):
            print("Path")
            dx, dy = animation.path[-1]
            if animation.centered:
                print("CENTERED")
                sys.exit(1)
            if animation.relative:
                shape.x = shape.ox+dx*Document.SCALE
                shape.y = shape.oy+dy*Document.SCALE
            else:
                shape.x = dx*Document.SCALE
                shape.y = dy*Document.SCALE
        if isinstance(animation, Scale):
            print("Scale")
        if isinstance(animation, Rotation):
            print("Rotation")

    def run_sequence(self, target, click=False):
        if target is None or target.id not in self.sequences:
            id = "main"
        else:
            id = target.id
        sequence = self.sequences[id]
        head = self.sequences_head[id]

        if head == len(sequence):
            if id == "main" and click:
                return Context.EXIT
            head = 0

        for animation in sequence[head:]:
            if animation.click and not click:
                break
            click = False
            head += 1
            self.apply(animation)

        self.sequences_head[id] = head

        if target is not None:
            if target.name == "_UPDATE":
                return Context.REFRESH
            if target.name == "_STOP":
                return Context.STOP
        return Context.CONTINUE

    def get_under(self, x, y):
        target = None
        for shape in self.visible:
            if isinstance(shape, Group):
                dx, dy = shape.ox-shape.x, shape.oy-shape.y
            else:
                dx = dy = 0
            if shape.visible and shape.contains(x+dx, y+dy):
                target = shape
        return target

    def click(self, x, y):
        target = self.get_under(x, y)
        print("CLICK", target)
        return self.run_sequence(target, True)