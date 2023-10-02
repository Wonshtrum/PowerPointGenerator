from pptgen import *
from pptgen.serializer import save_to_pptx
from pptgen.runner import tk_run

Text.DEFAULT_COLOR = (255, 255, 255)
Text.DEFAULT_SIZE = 10

D = 4
W = 1
Target = lambda s: Place(s, (tx+(s.z-int(s.z))*10*W, ty+int(s.z)*W), relative=False)
GREY = lambda x: (G(x), G(x), G(x))
G = lambda x: int(256*(x/256)**0.5)
Z = lambda a,b=0,c=0: a*D+b+(c/10 if a*D+b>=0 else -c/10)
UP = Animation.UP

tl = Timeline()

N_BITS = 8

tx = 0
ty = 10

w = 2
ox = 10
oy = 10

start = Shape(0, 0, w, w, (0, 255, 0))
tl.add(Place(start), on=start)
I = Shape(ox, oy+0*w, 3*w, w, GREY(180), z=Z(0,-1,0))
J = Shape(ox, oy+1*w, 3*w, w, GREY(200), z=Z(0,-1,.5))
K = Shape(ox, oy+2*w, 3*w, w, GREY(220), z=Z(0,-1,1))
reset = Shape(1*w, 0, w, w, (255, 200, 0), text="G")
SET_0 = Shape(2*w, 0, w, w, (255, 0, 0), text=0)
SET_1 = Shape(3*w, 0, w, w, (0, 255, 0), text=1)
tl.add(Place(SET_0), on=SET_0)
tl.add(Place(SET_1), on=SET_1)

for IJK in (I, J, K):
    tl.add(Target(IJK), on=start)
    tl.add(Place(IJK), on=IJK)
    tl.add(Appear(IJK), on=reset)

GATES_1 = [
    ("id",  lambda a: a),
    ("not",  lambda a: not a),
]
GATES_2 = [
    ("or",  lambda a,b: a | b),
    ("xor", lambda a,b: a ^ b),
    ("and", lambda a,b: a & b),
]
GATES_3 = [
    ("add", lambda a,b,c: (a ^ b ^ c, a & b | c & (a | b))),
    ("sub", lambda a,b,c: (a ^ b ^ c, (not a) & b | c & ((not a) | b))),
]

s_ox = ox
ox += 3*(3.5*w)
TARGET_MEM = Shape(ox, oy+3*w, w, 1, (0, 0, 200))
PTR = [
    Shape(ox, oy+(3+i)*w+1, w, w, (G(130+15*i), G(20*i), G(130+15*i)))
    for i in range(N_BITS)
]
TARGET_OPC = Shape(ox+w, oy+3*w, w, 1, (0, 0, 255))
OPC = [
    Shape(ox+w, oy+(3+i)*w+1, w, w, (G(20*i), G(130+15*i), G(130+15*i)), z=Z(i, 0, 0))
    for i in range(N_BITS)
]
for bit in OPC:
    tl.add(Target(bit), on=TARGET_OPC)
    tl.add(SlideIn(bit, UP), on=bit)

def ISA(ox, oy):
    S = Style((0, 0, 0), (255, 255, 255), 0.1)
    for i in range(183):
        x = i//8
        y = i%8
        ins = Shape(ox+x*w, oy+y*w, w, w, S, text=i)
        tl.add(Appear(ins), on=TARGET_OPC)
        for j, bit in enumerate(OPC):
            if i & 1<<j == 0:
                tl.add(Disappear(ins), on=bit)
ISA(ox+2*w, oy+3*w+1)
ox = s_ox

class Byte:
    def __init__(self, x, y, w, is_i=False, is_j=False, addr=None, reg=None):
        w2 = w/2
        Shape(x, y, 3*w, w*N_BITS+w, (200, 200, 255), z=Z(N_BITS+1))
        x += w2
        reset = Shape(x, y+w*N_BITS+w2, w, w2, (255, 0, 255), z=Z(N_BITS))
        tl.add(Place(reset), on=reset)
        if is_i:
            target_i = Shape(x, y, w2, w2, (0, 0, 200))
            tl.add(Target(reset), on=target_i)
        if is_j:
            target_j = Shape(x+w2, y, w2, w2, (0, 0, 255))
            tl.add(Target(reset), on=target_j)
        target_d = Shape(x+w, y, w, w2, (255, 0, 255))
        if is_j and addr is not None:
            for i,bit in enumerate(PTR):
                if 1<<i & addr == 0:
                    tl.add(Disappear(target_d), on=bit)
                    tl.add(Disappear(target_j), on=bit)
            tl.add(Appear(target_d), on=TARGET_MEM)
            tl.add(Appear(target_j), on=TARGET_MEM)
        y += w2

        self.bits = [None]*N_BITS
        for i in range(N_BITS):
            set_0 = Shape(x+2*w2, y+i*w, w2, w, (255, 0, 0), z=Z(i,2,0))
            set_1 = Shape(x+3*w2, y+i*w, w2, w, (0, 255, 0), z=Z(i,2,.5))
            tl.add(Appear(set_0), on=SET_0)
            tl.add(Disappear(set_0), on=SET_1)
            tl.add(Target(set_0), on=target_d)
            tl.add(Target(set_1), on=target_d)
            tl.add(Place(set_0), on=set_0)
            tl.add(Place(set_1), on=set_0)
            tl.add(Place(set_0), on=set_1)
            tl.add(Place(set_1), on=set_1)
            bit_i = bit_j = None
            if is_i:
                bit_i = Shape(x, y+i*w, w2, w, GREY(i*10), z=Z(i,0,0))
                tl.add(Disappear(I), on=bit_i)
                tl.add(Target(bit_i), on=target_i)
            if is_j:
                bit_j = Shape(x+w2, y+i*w, w2, w, GREY(i*10+20), z=Z(i,0,.5))
                tl.add(Disappear(J), on=bit_j)
                tl.add(Target(bit_j), on=target_j)
                if addr is not None:
                    tl.add(Disappear(OPC[i]), on=bit_j)
            for bit in (bit_i, bit_j):
                if bit is not None:
                    tl.add(Place(bit), on=bit)
                    tl.add(Place(bit), on=reset)
                    tl.add(SlideIn(bit, UP), on=set_1)
                    tl.add(Disappear(bit), on=set_0)
            self.bits[i] = (bit_i, bit_j, set_0, set_1)

dx = 4*w
for (name, f) in GATES_1:
    step = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    for IJ in (I, J):
        tl.add(SlideIn(IJ, UP), on=step)
    tl.add(Place(step), on=step)
    for i in (1, 0):
        r = f(i)
        n = i
        case = Shape(ox+dx, oy+i*w, w, w, (G(160+20*n), G(80+10*n), 0), text=r)
        tl.add(SlideOut(case, UP), on=reset)
        tl.add(Target(step), on=case)
        tl.add(SlideIn(case, UP), on=step)
        tl.add(Target(case), on=start)
        if i:
            tl.add(Disappear(case), on=I)
        tl.add(Target(SET_1 if r else SET_0), on=case)
    dx += 2*w

for (name, f) in GATES_2:
    step = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    for IJ in (I, J):
        tl.add(SlideIn(IJ, UP), on=step)
    tl.add(Place(step), on=step)
    for i in (1, 0):
        for j in (1, 0):
            r = f(i, j)
            n = i+2*j
            case = Shape(ox+dx+j*w, oy+i*w, w, w, (G(160+20*n), G(80+10*n), 0), text=r)
            tl.add(SlideOut(case, UP), on=reset)
            tl.add(Target(step), on=case)
            tl.add(SlideIn(case, UP), on=step)
            tl.add(Target(case), on=start)
            if i:
                tl.add(Disappear(case), on=I)
            if j:
                tl.add(Disappear(case), on=J)
            tl.add(Target(SET_1 if r else SET_0), on=case)
    dx += 3*w

for (name, f) in GATES_3:
    step = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    for IJ in (I, J):
        tl.add(SlideIn(IJ, UP), on=step)
    tl.add(Place(step), on=step)
    for i in (1, 0):
        for j in (1, 0):
            for k in (1, 0):
                r0, r1 = f(i, j, k)
                n = i+2*j+4*k
                case = Shape(ox+dx+(j+2*k)*w, oy+i*w, w, w, (G(80+20*n), G(40+10*n), 0), text=f"{r1}{r0}")
                tl.add(SlideOut(case, UP), on=reset)
                tl.add(Target(step), on=case)
                tl.add(SlideIn(case, UP), on=step)
                tl.add(Target(case), on=start)
                if i:
                    tl.add(Disappear(case), on=I)
                if j:
                    tl.add(Disappear(case), on=J)
                if k:
                    tl.add(Disappear(case), on=K)
                tl.add(Target(SET_1 if r0 else SET_0), on=case)
                if r1:
                    tl.add(SlideOut(K, UP), on=case)
                else:
                    tl.add(SlideIn(K, UP), on=case)
    dx += 5*w

for i in range(N_BITS):
    step = Shape(0, w, w, w, (200, 255, 200), z=Z(i, 1))
    tl.add(Target(start), on=step)
    tl.add(Place(step), on=step)
    tl.add(Target(step), on=reset)

for reg in range(3):
    i = reg
    Byte(ox+3.5*i*w, oy+3*w, w, is_i=True, is_j=True, reg=reg)
R = 32
ww = 1
for addr in range(64):
    i = addr%R
    j = addr//R
    Byte(ox+3*i*ww, oy+(N_BITS+5)*w+j*(N_BITS+1.5)*ww, ww, is_j=True, addr=addr)

shapes = Shape.dump()
slide = Slide("cpu", shapes, tl)
doc = Document("cpu", [slide])
#save_to_pptx(doc)

scale = 10/Document.SCALE
tk_run(slide, Document.WIDTH*scale, Document.HEIGHT*scale, scale, smart_refresh=False, validate_exit=True)
