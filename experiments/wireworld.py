from pptgen import *
from pptgen.serializer import save_to_pptx
from pptgen.runner import tk_run


Target = lambda shape: Place(shape, (tx, ty), relative=False)
Reset = lambda shape: SlideIn(shape, Animation.UP)


def in_bound(x, y, w, h):
    return x>=0 and y>=0 and x<w and y<h


DEBUG = 0
class Cell:
    def __init__(self, x, y, w):
        base = Shape(x, y, w, w, Style(None, WHITE, 0.1), z=5)
        wire = Shape(x, y, w, w, Style((255, 200, 0), WHITE, 0.1), z=4)
        tail = Shape(x, y, w, w, Style((255, 0, 0), WHITE, 0.1), z=3)
        head = Shape(x, y, w, w, Style((0, 0, 255), WHITE, 0.1), z=-1)

        self.base = base
        self.wire = wire
        self.tail = tail
        self.head = head

        mw = w/3
        self.counter = [
            Shape(DEBUG*(x+12*w), DEBUG*(y+(i+3)*mw), mw*3, mw, (100, 100, 100), z=0)
            for i in range(3)
        ]
        self.connect = [
            Shape(DEBUG*(x+i*mw+6*w), DEBUG*(y+j*mw), mw, mw, (0, 255, 0), z=0)
            for i in range(3)
            for j in range(3)
            if i != 1 or j != 1
        ]
        self.confirm = Shape(tx, ty, w, w, (0, 255, 255), z=2)
        self.delete = Shape(x, y, w, w, Style((255, 100, 0), WHITE, 0.1))

        for (i, _) in enumerate(self.counter):
            if i < 2:
                tl.add(Reset(self.counter[i+1]), on=_)
            tl.add(Disappear(_), on=_)

        reset = self.counter[-1]
        for _ in self.connect:
            tl.add(Reset(_), on=_)
            tl.add(Reset(self.confirm), on=_)
            for p in self.counter:
                tl.add(Target(p), on=_)
            tl.add(Reset(_), on=reset)

        tl.add(Disappear(self.confirm))
        tl.add(Disappear(self.confirm), on=reset)
        tl.add(Disappear(self.confirm), on=self.confirm)
        tl.add(Reset(head), on=self.confirm)

    def on_head(self):
        base, wire, tail, head, delete = self.base, self.wire, self.tail, self.head, self.delete

        for _ in self.counter:
            tl.add(Disappear(_), on=head)

        for _ in self.connect:
            tl.add(Reset(_), on=tail)
            tl.add(Reset(_), on=base)
            tl.add(Disappear(_), on=wire)
            tl.add(Disappear(_), on=self.confirm)

        tl.add(Appear(delete), on=head)
        tl.add(Disappear(self.delete), on=delete)
        tl.add(Disappear(tail), on=delete)

        tl.add(Appear(wire), on=base)
        tl.add(Appear(head), on=wire)
        tl.add(Reset(tail), on=head)
        tl.add(Appear(wire), on=tail)
        tl.add(Disappear(wire), on=wire)
        tl.add(Disappear(tail), on=tail)
        tl.add(Disappear(head), on=head)


WHITE = (255, 255, 255)

tl = Timeline()

n_rows = 15
n_cols = 20
w = 2
ox = w
oy = w
tx = 0
ty = oy

cells = [
        [Cell(ox+i*w, oy+j*w, w) for i in range(n_cols)]
        for j in range(n_rows)
    ]

for i in range(n_cols):
    for j in range(n_rows):
        cell = cells[j][i]
        c = 0
        for _i in range(3):
            for _j in range(3):
                if _i != 1 or _j != 1:
                    if in_bound(i+_i-1, j+_j-1, n_cols, n_rows):
                        neighbour = cells[j+_j-1][i+_i-1]
                        tl.add(Target(neighbour.connect[c]), on=cell.head)
                        cell.on_head()
                    c += 1


start = Shape(tx, ty, w, w, (0, 255, 0), z=-1)
update = Shape(tx, ty, w, w, (255, 0, 255), z=6, name="_UPDATE")
step = Shape(tx, ty, w, w, (255, 0, 255), z=-1)

tl.add(Appear(step), on=update)
tl.add(Disappear(step), on=step)
tl.add(Disappear(start), on=start)

for i in range(n_cols):
    for j in range(n_rows):
        cell = cells[j][i]
        tl.add(Target(cell.head), on=step)
        tl.add(Target(cell.tail), on=step)
        tl.add(Reset(cell.counter[0]), on=step)
        tl.add(Place(cell.delete, (0, 0), relative=False), on=start)
        for _ in cell.connect:
            tl.add(Place(_), on=start)


shapes = Shape.dump()
slide = Slide("wireworld", shapes, tl)
doc = Document("wireworld", [slide])
#save_to_pptx(doc)

scale = 10/Document.SCALE
tk_run(slide, Document.WIDTH*scale, Document.HEIGHT*scale, scale, smart_refresh=True)
