from pptgen import Document
from pptgen.animation import *
import sys

print = lambda *arg, **kwargs: None

class Context:
    def __init__(self, slide):
        self.slide = slide
        self.shapes = {shape.id:shape for shape in slide.shapes}
        self.timeline = slide.timeline
        self.sequences = slide.timeline.contexts
        self.sequences_head = {k:0 for k in slide.timeline.contexts.keys()}
        self.visible = list(reversed(sorted(slide.shapes, key=lambda shape:shape.z)))

        for shape in slide.shapes:
            shape.ox = shape.x
            shape.oy = shape.y
            shape.visible = True

        must_be = {}
        for animation in slide.timeline.contexts["main"]:
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
        if isinstance(animation, FadeOut):
            print("FadeOut")
            print("UNSUPPORTED")
            sys.exit(1)
        if isinstance(animation, SlideIn):
            print("SlideIn")
            shape.x = shape.ox
            shape.y = shape.oy
        if isinstance(animation, SlideOut):
            print("SlideOut")
        if isinstance(animation, Path):
            print("Path")
            dx, dy = animation.path[-1]
            if animation.centered:
                print("CENTERED")
                sys.exit(1)
            if animation.relative:
                print("Relative", dx, dy)
                shape.x = shape.ox+dx*Document.SCALE
                shape.y = shape.oy+dy*Document.SCALE
            else:
                shape.x = dx*Document.SCALE
                shape.y = dy*Document.SCALE
        if isinstance(animation, Scale):
            print("Scale")
        if isinstance(animation, Rotation):
            print("Rotation")

    def run_sequence(self, id, backend, click=False):
        if id not in self.sequences:
            id = "main"
        sequence = self.sequences[id]
        head = self.sequences_head[id]
        if head == len(sequence):
            if id == "main" and click:
                return True
            head = 0

        for animation in sequence[head:]:
            if animation.click and not click:
                break
            click = False
            head += 1
            self.apply(animation)

        self.sequences_head[id] = head
        backend.draw()
        return False

    def get_under(self, x, y):
        id = "main"
        for shape in self.visible:
            if shape.visible and shape.contains(x, y):
                id = shape.id
        return id

    def click(self, x, y, backend):
        id = self.get_under(x, y)
        print("CLICK", id)
        return self.run_sequence(id, backend, True)