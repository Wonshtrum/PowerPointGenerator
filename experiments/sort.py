from pptgen import *
from pptgen.serializer import save_to_pptx
from pptgen.runner import tk_run
from random import randrange
from capture import Recorder

def hsl_to_rgb(h, s, l):
    h /= 360
    s /= 100
    l /= 100

    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return int(r * 255), int(g * 255), int(b * 255)

tl = Timeline()
Text.DEFAULT_COLOR = (255, 255, 255)
Target = lambda s, click=False: Place(s, target, relative=False, click=click)
DTarget = lambda s, *args, **kwargs: Place(s, *args, **kwargs) if D else Target(s)
Outline = lambda c, w=.5: Style(outline=c, width=w)
D = False

tx = 0
ty = 10
target = (tx, ty)

N = 16
ox = 10
oy = N+1
w = 3
values = [None]*N
for i in range(N):
    H = randrange(0, N)
    #H = i
    values[i] = (
            Shape(tx, ty-(N-1)*(w-1), w-1, (H+1)*(w-1), hsl_to_rgb(i*360/(N+1), 100, 50), z=N+1),
            Shape(ox+i*w, oy+w-0.75, w-1, (H+1)*(w-1), Outline(hsl_to_rgb(i*360/(N+1), 100, 50), .2))
        )
    tl.add(Disappear(values[i][0]))
sg = [[None]*N for _ in range(N)]
cc = [None]*N
for i in range(N):
    x = ox+i*w
    cc[i] = c = Shape(x, oy, w-1, w-1, Outline(hsl_to_rgb(i*360/(N+1), 100, 50)), z=-2, name="_UPDATE")
    tl.add(Place(c), on=c)
    for j in range(N):
        s = Shape(x, oy-j-1, (w-1)/2, 0.75, hsl_to_rgb(j*360/(N+1), 100, 70), z=N-i)
        g = Shape(x+(w-1)/2, oy-j-1, (w-1)/2, 1, hsl_to_rgb(j*360/(N+1), 50, 50), z=-1)
        sg[i][j] = (s, g)
        if i != j:
            tl.add(Disappear(g))
        if i == 0:
            tl.add(Disappear(s))
        tl.add(Appear(s), on=values[j][0])
        tl.add(Appear(g), on=s)
        #tl.add(Appear(g), on=values[j])
        #tl.add(DTarget(values[j][1], (tx, oy+w-0.75), relative=False), on=g)
        tl.add(Appear(values[j][0]), on=g)
        tl.add(Disappear(g), on=g)
        tl.add(Disappear(values[j][0]), on=s)
        tl.add(Place(values[j][1], (x, oy+w-0.75), relative=False), on=s)
        tl.add(DTarget(s, (tx, oy-j-1), relative=False), on=c)
        tl.add(DTarget(g, (tx, oy-j-1), relative=False), on=c)
    for s0, g0 in sg[i]:
        for s1, g1 in sg[i]:
            tl.add(SlideOut(s1, Animation.UP), on=s0)
            tl.add(Place(g1), on=s0)
for i in range(N):
    for j in range(N):
        for k in range(N):
            tl.add(Disappear(sg[j][i][0]), on=sg[k][i][0])
            #tl.add(Disappear(sg[j][i][1]), on=sg[k][i][0])

stop = Shape(tx, ty, w, w)
shift = Shape(tx, ty, w-.5, w-.5, z=N*2+1)
r = Shape(tx, ty, w, w, (0, 255, 0), z=N*2+2)
for i in range(N-1):
    tl.add(Appear(shift), on=cc[i])
    for j in range(N-i-1):
        tl.add(Target(cc[j], click=True), on=r)
        tl.add(Target(cc[j+1]), on=r)
tl.add(Appear(stop, click=True), on=r)
tl.add(Appear(stop), on=stop)

for i in range(N-1):
    for j in range(N):
        tl.add(Place(values[j][0], (0, (i+1)*(w-1)), relative=True, click=j==0), on=shift)
tl.add(Disappear(shift, click=True), on=shift)
for j in range(N):
    tl.add(Place(values[j][0]), on=shift)

RECORD = True
recorder = Recorder()
def frame_callback(ctx):
    if not RECORD:
        return
    recorder.save_frame(ctx.can)
    print(len(recorder.frames))

shapes = Shape.dump()
slide = Slide("sort", shapes, tl)
doc = Document("sort", [slide])
#save_to_pptx(doc)
scale = 10/Document.SCALE
tk_run(slide, Document.WIDTH*scale, Document.HEIGHT*scale, scale, smart_refresh=RECORD, frame_callback=frame_callback)
recorder.save_video("bubble_sort_pptx")
