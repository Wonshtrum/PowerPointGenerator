from pptgen import *
from pptgen.serializer import save_to_pptx
from pptgen.runner import tk_run

Text.DEFAULT_COLOR = (255, 255, 255)
Text.DEFAULT_SIZE = 10

D = 4
Target = lambda s: Place(s, (tx+(s.z-int(s.z))*10*w, ty+int(s.z)*w), relative=False)
GREY = lambda x: (G(x), G(x), G(x))
G = lambda x: int(256*(x/256)**0.5)
Z = lambda a,b=0,c=0: a*D+b+(c/10 if a*D+b>=0 else -c/10)
UP = Animation.UP

tl = Timeline()

tx = 0
ty = 10

w = 3
ox = 10
oy = 10

start = Shape(0, 0, w, w, (0, 255, 0))
tl.add(Place(start), on=start)
I = Shape(ox, oy+0*w, 3*w, w, GREY(180), z=Z(0,-1,0))
J = Shape(ox, oy+1*w, 3*w, w, GREY(200), z=Z(0,-1,.5))
K = Shape(ox, oy+2*w, 3*w, w, GREY(220), z=Z(0,-1,1))
reset = Shape(ox, oy-1, 1, 1, (0, 0, 255))

for IJK in (I, J, K):
    tl.add(Target(IJK), on=start)
    tl.add(Place(IJK), on=IJK)
    tl.add(Appear(IJK), on=reset)

GATES_2 = [
    ("or",  lambda a,b: a | b),
    ("xor", lambda a,b: a ^ b),
    ("and", lambda a,b: a & b),
]
GATES_3 = [
    ("add", lambda a,b,c: (a ^ b ^ c, a & b | c & (a | b))),
    ("sub", lambda a,b,c: ((not a) & b | c & ((not a) | b), a ^ b ^ c)),
]

"""
0 0 0  0 0  0 0
0 0 1  0 1  1 1
0 1 0  0 1  1 1
0 1 1  1 0  0 1
1 0 0  0 1  1 0
1 0 1  1 0  0 0
1 1 0  1 0  0 0
1 1 1  1 1  1 1
"""

class Byte:
    N_BITS = 4
    def __init__(self, x, y, w, is_i=False, is_j=False):
        w2 = w/2
        Shape(x, y, 2*w+2, w*Byte.N_BITS+2, (200, 200, 255), z=Z(Byte.N_BITS))
        x += 1
        y += 1
        if is_i:
            target_i = Shape(x, y, w2, 1, (0, 0, 200))
        if is_j:
            target_j = Shape(x+w2, y, w2, 1, (0, 0, 255))
        target_d = Shape(x+w, y, w, 1, (255, 0, 255))

        self.bits = [None]*Byte.N_BITS
        for i in range(Byte.N_BITS):
            set_0 = Shape(x+2*w2, y+i*w, w2, w, (255, 0, 0), z=Z(i,2,0))
            set_1 = Shape(x+3*w2, y+i*w, w2, w, (0, 255, 0), z=Z(i,2,0))
            tl.add(Target(set_1), on=target_d)
            tl.add(Place(set_1), on=set_1)
            bit_i = bit_j = None
            if is_i:
                bit_i = Shape(x, y+i*w, w2, w, GREY(i*10), z=Z(i,0,0))
                tl.add(Disappear(I), on=bit_i)
                tl.add(Target(bit_i), on=target_i)
                tl.add(SlideOut(bit_i, UP), on=bit_i)
                tl.add(Appear(bit_i), on=set_1)
                tl.add(Disappear(bit_i), on=set_0)
            if is_j:
                bit_j = Shape(x+w2, y+i*w, w2, w, GREY(i*10+20), z=Z(i,0,.5))
                tl.add(Disappear(J), on=bit_j)
                tl.add(Target(bit_j), on=target_j)
                tl.add(Place(bit_j), on=bit_j)
                tl.add(Appear(bit_j), on=set_1)
                tl.add(Disappear(bit_j), on=set_0)
            self.bits[i] = (bit_i, bit_j, set_1)


#step = Shape(w, 0, w, w, (255, 200, 0), text="G")
reset = Shape(2*w, 0, w, w, (255, 0, 0), text="G")
dx = 4*w
for (name, f) in GATES_2:
    handle = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    step = Shape(ox+dx+w, oy-w, w, w, (255, 0, 0), text=name)
    for IJK in (I, J, K):
        tl.add(SlideIn(IJK, UP), on=step)
    tl.add(Place(step), on=step)
    for i in range(2):
        for j in range(2):
            r = f(i, j)
            n = i+2*j
            case = Shape(ox+dx+i*w, oy+j*w, w, w, (G(160+20*n), G(80+10*n), 0), text=r)
            #tl.add(Appear(case), on=handle)
            tl.add(SlideOut(case, UP), on=reset)
            tl.add(Target(step), on=case)
            tl.add(SlideIn(case, UP), on=step)
            tl.add(Target(case), on=start)
            if not i:
                tl.add(Disappear(case), on=I)
            if not j:
                tl.add(Disappear(case), on=J)
    dx += 3*w

for (name, f) in GATES_3:
    handle = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    step = Shape(ox+dx+w, oy-w, w, w, (255, 0, 0), text=name)
    for IJK in (I, J, K):
        tl.add(SlideIn(IJK, UP), on=step)
    tl.add(Place(step), on=step)
    for i in range(2):
        for j in range(2):
            for k in range(2):
                r0, r1 = f(i, j, k)
                n = i+2*j+4*k
                case = Shape(ox+dx+(2*i+k)*w, oy+j*w, w, w, (G(80+20*n), G(40+10*n), 0), text=f"{r1}{r0}")
                #tl.add(Appear(case), on=handle)
                tl.add(SlideOut(case, UP), on=reset)
                tl.add(Target(step), on=case)
                tl.add(SlideIn(case, UP), on=step)
                tl.add(Target(case), on=start)
                if not i:
                    tl.add(Disappear(case), on=I)
                if not j:
                    tl.add(Disappear(case), on=J)
                if not k:
                    tl.add(Disappear(case), on=K)
    dx += 5*w

for i in range(Byte.N_BITS):
    step = Shape(tx, ty+Z(i, 1, 0)*w, w, w, (200, 255, 200))
    tl.add(Target(start), on=step)
    tl.add(Disappear(step), on=step)
    tl.add(Appear(step), on=reset)

for i in range(2):
    Byte(ox+3*i*w, oy+3*w, w, is_i=True, is_j=True)
for i in range(8):
    Byte(ox+3*i*w, oy+(4+Byte.N_BITS)*w, w, is_j=True)

shapes = Shape.dump()
slide = Slide("cpu", shapes, tl)
doc = Document("cpu", [slide])
#save_to_pptx(doc)

scale = 10/Document.SCALE
tk_run(slide, Document.WIDTH*scale, Document.HEIGHT*scale, scale, smart_refresh=False)
