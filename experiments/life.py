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
        if DEBUG:
            w -= 1
            Shape(x+3*(w+1), y, w, w, (200, 255, 255), z=1)
            Shape(x+6*(w+1), y, w, w, (200, 255, 255), z=1)
        self.reset = Shape(x, y, w, w, (255, 255, 200, 0.5), z=-1)
        self.alive = Shape(x, y, w, w, (255, 0, 0), z=-1)
        self.die = Shape(tx, ty, w, w, (255, 255, 0), z=1)
        tl.add(Appear(self.alive), on=self.reset)
        tl.add(Disappear(self.alive, click=True), on=self.reset)
        tl.add(Place(self.alive, (0, 0)), on=self.alive)
        tl.add(Appear(self.die), on=self.alive)
        tl.add(Disappear(self.alive), on=self.die)
        tl.add(Disappear(self.die), on=self.die)

        if DEBUG:
            mh = w/4
        else:
            mh = w
        self.counter = [
            Shape(DEBUG*(x+6*(w+1)), DEBUG*(y+j*mh), w, mh, GREY(100+30*j))
            for j in range(4)
        ]
        mw = w/3
        self.connect = [
            Shape(tx, ty, w, w, (0, 255, 255))
            #Shape(DEBUG*(x+i*mw+3*(w+1)), DEBUG*(y+j*mw), mw, mw, (0, 255, 255))
            for i in range(3)
            for j in range(3)
            if i != 1 or j != 1
        ]

        for (i, _) in enumerate(self.counter):
            if i == 1:
                tl.add(Disappear(self.die), on=_)
            if i == 2:
                tl.add(Reset(self.alive), on=_)
            if i < 3:
                tl.add(Reset(self.counter[i+1]), on=_)
            else:
                tl.add(Disappear(self.alive), on=_)
                for c in self.connect:
                    tl.add(Disappear(c), on=_)
            tl.add(Disappear(_), on=_)

        for _ in self.connect:
            for p in self.counter:
                tl.add(Target(p), on=_)
            tl.add(Disappear(_), on=_)

WHITE = (255, 255, 255)
GREY = lambda x: (x, x, x)

tl = Timeline()

n_rows = 20
n_cols = 36
w = 2
ox = w
oy = w
tx = 0
ty = oy

cells = [[Cell(ox+i*w, oy+j*w, w) for i in range(n_cols)] for j in range(n_rows)]

WRAP = False
for i in range(n_cols):
    for j in range(n_rows):
        cell = cells[j][i]
        c = 0
        for _i in range(3):
            for _j in range(3):
                if _i != 1 or _j != 1:
                    if WRAP or in_bound(i+_i-1, j+_j-1, n_cols, n_rows):
                        neighbour = cells[(j+_j-1)%n_rows][(i+_i-1)%n_cols]
                        tl.add(Appear(neighbour.connect[7-c]), on=cell.alive)
                    c += 1

_ = False
O = True
pattern = [
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,O,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,O,_,O,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,O,O,_,_,_,_,_,_,O,O,_,_,_,_,_,_,_,_,_,_,_,_,O,O],
    [_,_,_,_,_,_,_,_,_,_,_,O,_,_,_,O,_,_,_,_,O,O,_,_,_,_,_,_,_,_,_,_,_,_,O,O],
    [O,O,_,_,_,_,_,_,_,_,O,_,_,_,_,_,O,_,_,_,O,O,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [O,O,_,_,_,_,_,_,_,_,O,_,_,_,O,_,O,O,_,_,_,_,O,_,O,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,O,_,_,_,_,_,O,_,_,_,_,_,_,_,O,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,O,_,_,_,O,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,O,O,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
]

gen = Shape(w, 0, w, w, (0, 0, 255))
for j, line in enumerate(pattern):
    for i, cell in enumerate(line):
        if cell:
            tl.add(Appear(cells[j][i].alive), on=gen)

start = Shape(tx, ty, w, w, (0, 255, 0), z=-1)
step = Shape(tx, ty, w, w, (255, 0, 255), z=2)
update = Shape(tx, ty, w, w, (0, 0, 0), z=1, name="_UPDATE")

tl.add(Disappear(start), on=start)
tl.add(Disappear(update), on=update)
tl.add(Appear(update), on=step)
for i in range(n_cols):
    for j in range(n_rows):
        cell = cells[j][i]
        tl.add(Disappear(cell.reset), on=start)
        for _ in cell.connect:
            tl.add(Disappear(_), on=start)
        tl.add(Reset(cell.counter[0]), on=step)
        for _ in cell.counter[1:]:
            tl.add(Disappear(_), on=step)
        tl.add(Target(cell.alive), on=step)

shapes = Shape.dump()
slide = Slide("game_of_life", shapes, tl)
doc = Document("game_of_life", [slide])
#save_to_pptx(doc)

scale = 10/Document.SCALE
tk_run(slide, Document.WIDTH*scale, Document.HEIGHT*scale, scale, smart_refresh=True)
