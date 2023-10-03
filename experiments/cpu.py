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

#====================================================================

N_BITS = 8
N_REGS = 3
N_BYTES = 64

tx = 0
ty = 10

w = 2
ox = 10
oy = 10

#====================================================================

START = Shape(0, 0, w, w, (0, 255, 0))
tl.add(Place(START), on=START)

GATE_RESET = Shape(1*w, 0, w, w, (255, 200, 0), text="G")
tl.add(Place(GATE_RESET), on=GATE_RESET)

SET_0 = Shape(2*w, 0, w, w, (255, 0, 0), text=0)
SET_1 = Shape(3*w, 0, w, w, (0, 255, 0), text=1)
tl.add(Place(SET_0), on=SET_0)
tl.add(Place(SET_1), on=SET_1)

I = Shape(ox, oy+0*w, 3*w, w, GREY(180), z=Z(0,-1,0))
J = Shape(ox, oy+1*w, 3*w, w, GREY(200), z=Z(0,-1,.5))
K = Shape(ox, oy+2*w, 3*w, w, GREY(220), z=Z(0,-1,1))
for IJK in (I, J, K):
    tl.add(Target(IJK), on=START)
    tl.add(Place(IJK), on=IJK)
    if IJK != K:
        tl.add(Appear(IJK), on=GATE_RESET)

#====================================================================

class Gate:
    def __init__(self, name, f):
        self.name = name
        self.f = f
    def call(self, ins):
        tl.add(Target(GATE_RESET), on=ins)
        tl.add(Target(self.step), on=ins)

GATES_1 = [
    Gate("id",  lambda a: a),
    Gate("not", lambda a: not a),
]
GATES_2 = [
    Gate("or",  lambda a,b: a | b),
    Gate("xor", lambda a,b: a ^ b),
    Gate("and", lambda a,b: a & b),
]
GATES_3 = [
    Gate("add", lambda a,b,c: (a ^ b ^ c, a & b | c & (a | b))),
    Gate("sub", lambda a,b,c: (a ^ b ^ c, (not a) & b | c & ((not a) | b))),
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

isa_ox = ox
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
            tl.add(Place(target_i), on=target_i)
            self.target_i = target_i
        if is_j:
            target_j = Shape(x+w2, y, w2, w2, (0, 0, 255))
            tl.add(Target(reset), on=target_j)
            tl.add(Place(target_j), on=target_j)
            self.target_j = target_j
        target_d = Shape(x+w, y, w, w2, (255, 0, 255))
        tl.add(Place(target_d), on=target_d)
        self.target_d = target_d
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

    def is_dest(self, ins):
        tl.add(Target(self.target_d), on=ins)
    def is_src_i(self, ins):
        tl.add(Target(self.target_i), on=ins)
    def is_src_j(self, ins):
        tl.add(Target(self.target_j), on=ins)

dx = 4*w
for gate in GATES_1:
    name = gate.name
    f = gate.f
    step = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    gate.step = step
    for IJ in (I, J):
        tl.add(SlideIn(IJ, UP), on=step)
    tl.add(Place(step), on=step)
    for i in (1, 0):
        r = f(i)
        n = i
        case = Shape(ox+dx, oy+i*w, w, w, (G(160+20*n), G(80+10*n), 0), text=r)
        tl.add(SlideOut(case, UP), on=GATE_RESET)
        tl.add(Target(step), on=case)
        tl.add(SlideIn(case, UP), on=step)
        tl.add(Target(case), on=START)
        if i:
            tl.add(Disappear(case), on=I)
        tl.add(Target(SET_1 if r else SET_0), on=case)
    dx += 2*w

for gate in GATES_2:
    name = gate.name
    f = gate.f
    step = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    gate.step = step
    for IJ in (I, J):
        tl.add(SlideIn(IJ, UP), on=step)
    tl.add(Place(step), on=step)
    for i in (1, 0):
        for j in (1, 0):
            r = f(i, j)
            n = i+2*j
            case = Shape(ox+dx+j*w, oy+i*w, w, w, (G(160+20*n), G(80+10*n), 0), text=r)
            tl.add(SlideOut(case, UP), on=GATE_RESET)
            tl.add(Target(step), on=case)
            tl.add(SlideIn(case, UP), on=step)
            tl.add(Target(case), on=START)
            if i:
                tl.add(Disappear(case), on=I)
            if j:
                tl.add(Disappear(case), on=J)
            tl.add(Target(SET_1 if r else SET_0), on=case)
    dx += 3*w

for gate in GATES_3:
    name = gate.name
    f = gate.f
    step = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    gate.step = step
    for IJ in (I, J):
        tl.add(SlideIn(IJ, UP), on=step)
    tl.add(Place(step), on=step)
    for i in (1, 0):
        for j in (1, 0):
            for k in (1, 0):
                r0, r1 = f(i, j, k)
                n = i+2*j+4*k
                case = Shape(ox+dx+(j+2*k)*w, oy+i*w, w, w, (G(80+20*n), G(40+10*n), 0), text=f"{r1}{r0}")
                tl.add(SlideOut(case, UP), on=GATE_RESET)
                tl.add(Target(step), on=case)
                tl.add(SlideIn(case, UP), on=step)
                tl.add(Target(case), on=START)
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


"""
NOP,

LDX #, LDY #, LDA #, LDX ?, LDY ?, LDA ?, LDX ?Y, LDY ?X, LDA ?X, LDA ?Y,
STX ?, STY ?, STA ?, STX ?Y, STY ?X, STA ?X, STA ?Y,

CPX #, CPY #, CPA #, CPX ?, CPY ?, CPA ?, CPA ?X, CPA ?Y,

TXA, TXY, TYA, TYX, TAX, TAY,

ORA #, ORA X, ORA Y, ORA ?, ORA ?X, ORA ?Y,
XOR #, XOR X, XOR Y, XOR ?, XOR ?X, XOR ?Y,
AND #, AND X, AND Y, AND ?, AND ?X, AND ?Y,
ADD #, ADD X, ADD Y, ADD ?, ADD ?X, ADD ?Y,
SUB #, SUB X, SUB Y, SUB ?, SUB ?X, SUB ?Y,

NOT A, NOT X, NOT Y, NOT ?, NOT ?X, NOT ?Y,
INC A, INC X, INC Y, INC ?, INC ?X, INC ?Y,
DEC A, DEC X, DEC Y, DEC ?, DEC ?X, DEC ?Y,

JMP #, JPX, JPY, JPA,
RET,

CLC, SEC,
BCC, BCS, BEQ, BNE,

PHP, PHA, PHX, PHY,
PLP, PLA, PLX, PLY,
"""
instruction_count = 0
def instruction(ox, oy, name):
    global instruction_count
    S = Style((0, 0, 0), (255, 255, 255), 0.1)
    i = instruction_count
    x = i//8
    y = i%8
    ins = Shape(ox+3*x*w, oy+y*w, 3*w, w, S, text=name)
    tl.add(Appear(ins), on=TARGET_OPC)
    for j, bit in enumerate(OPC):
        if i & 1<<j == 0:
            tl.add(Disappear(ins), on=bit)
    instruction_count += 1
    return ins

def ISA(ox, oy):
    REGS_XY = ((REG_X, "X"), (REG_Y, "Y"))
    REGS_XYA = ((REG_X, "X"), (REG_Y, "Y"), (REG_A, "A"))
    set_carry = lambda ins: tl.add(Disappear(K), on=ins)
    clr_carry = lambda ins: tl.add(Appear(K), on=ins)
    for gate in (*GATES_2, *GATES_3):
        instruction(ox, oy, f"{gate.name} #")
        instruction(ox, oy, f"{gate.name} ?")
        for reg, reg_name in REGS_XY:
            ins = instruction(ox, oy, f"{gate.name} {reg_name}")
            REG_A.is_dest(ins)
            REG_A.is_src_i(ins)
            reg.is_src_j(ins)
            gate.call(ins)
            instruction(ox, oy, f"{gate.name} ?{reg_name}")
        instruction(ox, oy, "")
        instruction(ox, oy, "")

    for gate, op_name in ((GATES_1[1], "not"), (GATES_3[0], "inc"), (GATES_3[1], "dec")):
        for reg, reg_name in REGS_XYA:
            ins = instruction(ox, oy, f"{op_name} {reg_name}")
            reg.is_dest(ins)
            reg.is_src_i(ins)
            gate.call(ins)
            if op_name != "NOT":
                set_carry(ins)
        ins = instruction(ox, oy, f"{op_name} ?")
        for reg, reg_name in REGS_XY:
            ins = instruction(ox, oy, f"{op_name} ?{reg_name}")
        instruction(ox, oy, "")
        instruction(ox, oy, "")

    mv = GATES_1[0]
    for src, src_name in REGS_XYA:
        for dst, dst_name in REGS_XYA:
            if src == dst: continue
            ins = instruction(ox, oy, f"mv {src_name}, {dst_name}")
            dst.is_dest(ins)
            src.is_src_i(ins)
            mv.call(ins)
    ins = instruction(ox, oy, "CLC")
    clr_carry(ins)
    ins = instruction(ox, oy, "SEC")
    set_carry(ins)

for i in range(N_BITS):
    step = Shape(0, w, w, w, (200, 255, 200), z=Z(i, 1))
    tl.add(Target(START), on=step)
    tl.add(Place(step), on=step)
    tl.add(Target(step), on=GATE_RESET)

REGS = [None]*N_REGS
for reg in range(N_REGS):
    i = reg
    REGS[i] = Byte(ox+3.5*i*w, oy+3*w, w, is_i=True, is_j=True, reg=reg)
REG_X = REGS[0]
REG_Y = REGS[1]
REG_A = REGS[2]

R = 32
ww = 1
BYTES = [None]*N_BYTES
for addr in range(N_BYTES):
    i = addr%R
    j = addr//R
    BYTES[addr] = Byte(ox+3*i*ww, oy+(N_BITS+5)*w+j*(N_BITS+1.5)*ww, ww, is_j=True, addr=addr)

ISA(isa_ox+2*w, oy+3*w+1)

shapes = Shape.dump()
slide = Slide("cpu", shapes, tl)
doc = Document("cpu", [slide])
#save_to_pptx(doc)

scale = 10/Document.SCALE
tk_run(slide, Document.WIDTH*scale, Document.HEIGHT*scale, scale, smart_refresh=False, validate_exit=True)