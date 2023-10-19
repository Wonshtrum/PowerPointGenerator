from pptgen import *
from pptgen.serializer import save_to_pptx
from pptgen.runner import tk_run

Text.DEFAULT_COLOR = (255, 255, 255)
Text.DEFAULT_SIZE = 10

D = 4
W = 0
Target = lambda s: Place(s, (tx+(s.z-int(s.z))*10*W, ty+int(s.z)*W), relative=False)
#Target = lambda s: Place(s, (tx+(s.z-int(s.z))*10*W, ty+int(s.z)*W), relative=False)
GREY = lambda x: (G(x), G(x), G(x))
G = lambda x: int(256*(x/256)**0.5)
Z = lambda a,b=0,c=0: a*D+b+(c/10 if a*D+b>=0 else -c/10)
UP = Animation.UP

tl = Timeline()

#====================================================================

N_BITS = 8
N_REGS = 3
N_BYTES = 8

tx = 0
ty = 10

w = 2
ox = 10
oy = 10

#====================================================================

START = Shape(0, 0, w, w, (0, 255, 0), text="S")
tl.add(Place(START), on=START)

SET_0 = Shape(1*w, 0, w, w, (255, 0, 0), text=0)
SET_1 = Shape(2*w, 0, w, w, (0, 255, 0), text=1)
tl.add(Place(SET_0), on=SET_0)
tl.add(Place(SET_1), on=SET_1)

GATE_RESET = Shape(3*w, 0, w, w, (180, 0, 0), text="G")
OP_RESET = Shape(4*w, 0, w, w, (180, 0, 0), text="OP")
J_RESET = Shape(5*w, 0, w, w, (180, 0, 0), text="J")
D_RESET = Shape(6*w, 0, w, w, (180, 0, 0), text="D")
IP_RESET = Shape(7*w, 0, w, w, (180, 0, 0), text="IP")
tl.add(Place(GATE_RESET), on=GATE_RESET)
tl.add(Place(OP_RESET), on=OP_RESET)
tl.add(Place(J_RESET), on=J_RESET)
tl.add(Place(D_RESET), on=D_RESET)
tl.add(Place(IP_RESET), on=IP_RESET)

I = Shape(ox+0*w, oy+w, w, w, GREY(180), z=Z(0,-1,0))
J = Shape(ox+1*w, oy+w, w, w, GREY(200), z=Z(0,-1,.5))
K = Shape(ox+2*w, oy+w, w, w, GREY(220), z=Z(0,-1,1))
for IJK in (I, J, K):
    tl.add(Target(IJK), on=START)
    tl.add(Place(IJK), on=IJK)
    if IJK != K:
        tl.add(Appear(IJK), on=GATE_RESET)

ZF = Shape(ox, oy, 3*w, w, (250, 0, 0), z=Z(0,-1,0))
tl.add(Place(ZF), on=ZF)
tl.add(Appear(ZF), on=GATE_RESET)
tl.add(Disappear(ZF), on=SET_1)

#====================================================================

class Gate:
    def __init__(self, name, f):
        self.name = name
        self.f = f
    def call(self, ins, wait=False):
        tl.add(Target(GATE_RESET), on=ins)
        tl.add(Target(self.step), on=ins)
        if wait:
            tl.add(Disappear(GATE_RESET), on=ins)
            tl.add(Disappear(self.step), on=ins)

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
    Gate("isub", lambda b,a,c: (a ^ b ^ c, (not a) & b | c & ((not a) | b))),
]

#====================================================================

s_ox = ox

ox += 3*(3.5*w)

OP_MOD = Shape(ox, oy+3*w, 4*w, 1, (255, 0, 255))

TARGET_OPC = Shape(ox+2*w, oy+3*w+1, 2*w, w, (0, 0, 200), text="OPC", z=Z(N_BITS, 1, 0))
TARGET_IMM = Shape(ox+2*w, oy+4*w+1, 2*w, w, (0, 0, 200), text="IMM", z=Z(0, 0, 0))
TARGET_LD = Shape(ox+2*w, oy+5*w+1, 2*w, w, (0, 0, 200), text="LD", z=Z(N_BITS, 1, 0))
TARGET_ST = Shape(ox+2*w, oy+6*w+1, 2*w, w, (0, 0, 200), text="ST", z=Z(N_BITS, 1, 0))
TARGET_LS = Shape(ox+2*w, oy+7*w+1, 2*w, w, (0, 0, 200), text="LS", z=Z(N_BITS, 1, 0))
TARGET_IP = Shape(ox+2*w, oy+8*w+1, 2*w, w, (0, 0, 200), text="IP", z=Z(N_BITS, 1, 0))
TARGET_NOP = Shape(ox+2*w, oy+9*w+1, 2*w, w, (0, 0, 200), text="NOP", z=Z(N_BITS, 1, 0))
w2 = w/2
OPC = [
    Shape(ox, oy+(3+i)*w+1, w2, w, (G(20*i), G(130+15*i), G(130+15*i)), z=Z(i, 0, 0))
    for i in range(N_BITS)
]
PTR = [
    Shape(ox+w2, oy+(3+i)*w+1, w2, w, (G(20+20*i), G(20+20*i), G(145+15*i)))
    for i in range(N_BITS)
]
RIP = [
    Shape(ox+w, oy+(3+i)*w+1, w2, w, (G(110+20*i), G(90+15*i), 0))
    for i in range(N_BITS)
]
for bit in (*PTR, *OPC):
    tl.add(SlideOut(bit, UP), on=J_RESET)
    tl.add(SlideOut(bit, UP), on=D_RESET)
    tl.add(SlideOut(bit, UP), on=bit)
for bit in RIP:
    tl.add(SlideOut(bit, UP), on=IP_RESET)
    tl.add(SlideOut(bit, UP), on=J_RESET)
    tl.add(SlideOut(bit, UP), on=bit)
    tl.add(Target(bit), on=TARGET_IP)
for bit in PTR:
    tl.add(Target(bit), on=TARGET_LD)
    tl.add(Target(bit), on=TARGET_ST)
    tl.add(Target(bit), on=TARGET_LS)
for bit in OPC:
    tl.add(Target(bit), on=TARGET_OPC)
TARGETS = (TARGET_OPC, TARGET_IMM, TARGET_LD, TARGET_ST, TARGET_LS, TARGET_IP, TARGET_NOP)
for t1 in TARGETS:
    tl.add(Appear(t1, click=True), on=OP_MOD)
    for t2 in TARGETS:
        if t1 != t2:
            tl.add(Disappear(t2), on=OP_MOD)

tl.add(Place(TARGET_OPC), on=TARGET_OPC)
tl.add(Disappear(TARGET_IMM), on=TARGET_IMM)
tl.add(Disappear(TARGET_LD), on=TARGET_LD)
tl.add(Disappear(TARGET_ST), on=TARGET_ST)
tl.add(Disappear(TARGET_LS), on=TARGET_LS)
tl.add(Disappear(TARGET_IP), on=TARGET_IP)
tl.add(Disappear(TARGET_NOP), on=TARGET_NOP)
tl.add(Appear(TARGET_IMM), on=TARGET_LD)
tl.add(Appear(TARGET_IMM), on=TARGET_LS)
tl.add(Appear(TARGET_IMM), on=TARGET_ST)
tl.add(SlideIn(TARGET_OPC, UP), on=TARGET_IMM)
tl.add(SlideIn(TARGET_OPC, UP), on=TARGET_IP)
tl.add(SlideIn(TARGET_OPC, UP), on=TARGET_NOP)
tl.add(Appear(GATE_RESET), on=TARGET_IMM)

isa_ox = ox
isa_oy = oy
ox = s_ox

#====================================================================

BCC = Shape(ox+3*w, oy+0*w, w, w, (0, 255, 0), text="CF")
BCS = Shape(ox+4*w, oy+0*w, w, w, (255, 0, 0), text="CF")
BEQ = Shape(ox+3*w, oy+1*w, w, w, (0, 255, 0), text="ZF")
BNE = Shape(ox+4*w, oy+1*w, w, w, (255, 0, 0), text="ZF")

for b in (BCS, BCC, BEQ, BNE):
    tl.add(SlideIn(TARGET_NOP, UP), on=b)
    tl.add(Disappear(TARGET_IP), on=b)
    tl.add(SlideIn(b, UP), on=b)
    tl.add(SlideIn(b, UP), on=TARGET_IP)
    tl.add(SlideIn(b, UP), on=TARGET_NOP)

tl.add(Disappear(BCC), on=K)
tl.add(Appear(BCS), on=K)
tl.add(Disappear(BEQ), on=ZF)
tl.add(Appear(BNE), on=ZF)

#====================================================================

class Byte:
    def __init__(self, x, y, w, is_i=False, is_j=False, addr=None, reg=None):
        w2 = w/2
        #self.ip = Shape(x, y, w2, w, (200, 50, 200))
        if addr is not None:
            self.ip = Group(
                    Shape(tx, ty, 4*w, 2*w, (240, 200, 0), text=addr),
                    Shape(x, y, 3*w, w*N_BITS+w, (255, 250, 120)), z=Z(N_BITS+1),
                    name="_UPDATE"
            )
            target_ip = Shape(x, y, w2, w, (240, 200, 0))
            tl.add(SlideIn(target_ip, UP), on=IP_RESET)
            tl.add(Disappear(self.ip), on=TARGET_IP)
            tl.add(Appear(self.ip), on=target_ip)
            self.target_ip = target_ip
        Shape(x, y, 3*w, w*N_BITS+w, (230, 230, 255), z=Z(N_BITS+1))
        x += w2
        reset = Shape(x, y+w*N_BITS+w2, w, w2, (255, 0, 255), z=Z(N_BITS))
        tl.add(Place(reset), on=reset)
        target_d = Shape(x+w, y, w, w2, (255, 0, 255), z=Z(0, 1, 0))
        tl.add(Place(target_d), on=target_d)
        self.target_d = target_d
        if is_i:
            target_i = Shape(x, y, w2, w2, (0, 0, 200), z=Z(0, 1, 0))
            tl.add(Target(reset), on=target_i)
            tl.add(Place(target_i), on=target_i)
            self.target_i = target_i
            if reg is not None:
                tl.add(Appear(target_i), on=TARGET_IMM)
                tl.add(Appear(target_d), on=TARGET_IMM)
        if is_j:
            target_j = Shape(x+w2, y, w2, w2, (0, 0, 255), z=Z(0, 1, 0))
            tl.add(Target(reset), on=target_j)
            tl.add(Place(target_j), on=target_j)
            self.target_j = target_j
            if addr is not None:
                for i in range(N_BITS):
                    if 1<<i & addr == 0:
                        tl.add(Disappear(target_d), on=PTR[i])
                        tl.add(Disappear(target_j), on=PTR[i])
                        tl.add(Disappear(target_ip), on=RIP[i])
                tl.add(Target(IP_RESET), on=target_ip)
                tl.add(SlideIn(target_d, UP), on=D_RESET)
                tl.add(SlideIn(target_j, UP), on=J_RESET)
                tl.add(Target(target_d), on=TARGET_ST)
                tl.add(Target(target_j), on=TARGET_LD)
                tl.add(Target(target_d), on=TARGET_LS)
                tl.add(Target(target_j), on=TARGET_LS)
                tl.add(Target(target_ip), on=TARGET_IP)
            tl.add(Target(D_RESET), on=target_d)
            tl.add(Target(J_RESET), on=target_j)
            if reg is not None:
                tl.add(Appear(target_j), on=TARGET_IMM)

        y += w2
        self.bits = [None]*N_BITS
        for i in range(N_BITS):
            set_0 = Shape(x+2*w2, y+i*w, w2, w, (255, 0, 0), z=Z(i,2,0))
            set_1 = Shape(x+3*w2, y+i*w, w2, w, (0, 255, 0), z=Z(i,2,.5))
            tl.add(Appear(set_0), on=SET_0)
            tl.add(Disappear(set_0), on=SET_1)
            tl.add(Target(set_0), on=target_d)
            tl.add(Target(set_1), on=target_d)
            tl.add(Place(set_0), on=set_1)
            tl.add(Place(set_1), on=set_1)
            tl.add(Place(set_0), on=set_0)
            tl.add(Place(set_1), on=set_0)
            bit_i = bit_j = None
            if is_i:
                bit_i = Shape(x, y+i*w, w2, w, GREY(i*10), z=Z(i,0,0))
                tl.add(SlideIn(bit_i, UP), on=set_1)
                tl.add(Disappear(I), on=bit_i)
                tl.add(Target(bit_i), on=target_i)
            if is_j:
                bit_j = Shape(x+w2, y+i*w, w2, w, GREY(i*10+20), z=Z(i,0,.5))
                tl.add(SlideIn(bit_j, UP), on=set_1)
                tl.add(Disappear(J), on=bit_j)
                tl.add(Target(bit_j), on=target_j)
                tl.add(Appear(RIP[i]), on=bit_j)
                if addr is not None:
                    tl.add(Appear(OPC[i]), on=bit_j)
                tl.add(Appear(PTR[i]), on=bit_j)
            for bit in (bit_i, bit_j):
                if bit is not None:
                    tl.add(Place(bit), on=bit)
                    tl.add(Place(bit), on=reset)
                    tl.add(Disappear(bit), on=set_0)
                    pass
            tl.move(reset)
            if is_i:
                tl.move(target_i)
            if is_j:
                tl.move(target_j)
            self.bits[i] = (bit_i, bit_j, set_0, set_1)

    def is_dest(self, ins, wait=False):
        tl.add(Target(self.target_d), on=ins)
        if wait:
            tl.add(Disappear(self.target_d), on=ins)
    def is_src_i(self, ins, wait=False):
        tl.add(Target(self.target_i), on=ins)
        if wait:
            tl.add(Disappear(self.target_i), on=ins)
    def is_src_j(self, ins, wait=False):
        tl.add(Target(self.target_j), on=ins)
        if wait:
            tl.add(Disappear(self.target_j), on=ins)

dx = 6*w
for gate in GATES_1:
    name = gate.name
    f = gate.f
    step = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    tl.add(Appear(step), on=TARGET_IMM)
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
            tl.add(Disappear(case), on=J)
        tl.add(Target(SET_1 if r else SET_0), on=case)
    dx += 2*w

for gate in GATES_2:
    name = gate.name
    f = gate.f
    step = Shape(ox+dx, oy-w, w, w, (0, 0, 0), text=name)
    tl.add(Appear(step), on=TARGET_IMM)
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
    tl.add(Appear(step), on=TARGET_IMM)
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

#====================================================================

"""
NOP,
                     STX ?, STY ?, STA ?, STA ?X, STA ?Y,
LDX #, LDY #, LDA #, LDX ?, LDY ?, LDA ?, LDA ?X, LDA ?Y,

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
    S = Style((0, 0, 0, 0.5), (255, 255, 255), 0.1)
    i = instruction_count
    x = i//8
    y = i%8
    ins = Shape(ox+2.5*x*w, oy+y*w, 2.5*w, w, S, text=name, z=Z(N_BITS))
    tl.add(Target(OP_RESET), on=ins)
    tl.add(SlideIn(ins, UP), on=OP_RESET)
    tl.add(Target(ins), on=TARGET_OPC)
    for j, bit in enumerate(OPC):
        if i & 1<<j == 0:
            tl.add(Disappear(ins), on=bit)
    instruction_count += 1
    return ins

def set_carry(ins, force=True):
    if force:
        tl.add(Disappear(K), on=ins)
def clr_carry(ins, force=True):
    if force:
        tl.add(Appear(K), on=ins)
def immediate(ins, wait=True):
    tl.add(Disappear(TARGET_OPC), on=ins)
    if wait:
        tl.add(SlideIn(TARGET_IMM, UP), on=ins)
    else:
        tl.add(Appear(TARGET_IMM), on=ins)
def load(ins, wait=True):
    tl.add(Disappear(TARGET_OPC), on=ins)
    if wait:
        tl.add(SlideIn(TARGET_LD, UP), on=ins)
    else:
        tl.add(Target(D_RESET), on=ins)
        tl.add(Appear(TARGET_LD), on=ins)
def store(ins, wait=True):
    tl.add(Disappear(TARGET_OPC), on=ins)
    if wait:
        tl.add(SlideIn(TARGET_ST, UP), on=ins)
    else:
        tl.add(Target(D_RESET), on=ins)
        tl.add(Appear(TARGET_ST), on=ins)
def load_store(ins, wait=True):
    tl.add(Disappear(TARGET_OPC), on=ins)
    if wait:
        tl.add(SlideIn(TARGET_LS, UP), on=ins)
    else:
        tl.add(Target(D_RESET), on=ins)
        tl.add(Appear(TARGET_LS), on=ins)
def jump(ins, wait=True):
    tl.add(Disappear(TARGET_OPC), on=ins)
    if wait:
        tl.add(SlideIn(TARGET_IP, UP), on=ins)
    else:
        tl.add(Target(IP_RESET), on=ins)
        tl.add(Appear(TARGET_IP), on=ins)
def branch(ins, b):
    f, v = { BCC: (K, False), BCS: (K, True), BEQ: (ZF, False), BNE: (ZF, True) }[b]
    if v:
        tl.add(Disappear(b), on=ins)
    tl.add(Target(b), on=ins)
    tl.add(Target(f), on=ins)
def fin(ins):
    ins.style.fill.alpha = 0
def ISA(ox, oy):
    REGS_XY = ((REG_X, "X"), (REG_Y, "Y"))
    REGS_XYA = ((REG_X, "X"), (REG_Y, "Y"), (REG_A, "A"))
    for gate in (*GATES_2, *GATES_3):
        for reg, reg_name in REGS_XY:
            ins = instruction(ox, oy, f"{gate.name} {reg_name}")
            REG_A.is_dest(ins)
            REG_A.is_src_i(ins)
            reg.is_src_j(ins)
            gate.call(ins)
            fin(ins)
        ins = instruction(ox, oy, f"{gate.name} #")
        REG_A.is_dest(ins, wait=True)
        REG_A.is_src_i(ins, wait=True)
        immediate(ins)
        gate.call(ins, wait=True)
        fin(ins)
        ins = instruction(ox, oy, f"{gate.name} ?")
        REG_A.is_dest(ins, wait=True)
        REG_A.is_src_i(ins, wait=True)
        load(ins)
        gate.call(ins, wait=True)
        fin(ins)
        for reg, reg_name in REGS_XY:
            ins = instruction(ox, oy, f"{gate.name} ?{reg_name}")
            REG_A.is_dest(ins, wait=True)
            REG_A.is_src_i(ins, wait=True)
            reg.is_src_j(ins)
            load(ins, wait=False)
            gate.call(ins, wait=True)
            fin(ins)
        instruction(ox, oy, "")
        instruction(ox, oy, "")

    for gate, op_name, carry in ((GATES_1[1], "not", False), (GATES_3[0], "inc", True), (GATES_3[2], "dec", True)):
        for reg, reg_name in REGS_XYA:
            ins = instruction(ox, oy, f"{op_name} {reg_name}")
            reg.is_dest(ins)
            reg.is_src_j(ins)
            immediate(ins, wait=False)
            set_carry(ins, carry)
            gate.call(ins)
            fin(ins)
        ins = instruction(ox, oy, f"{op_name} ?")
        load_store(ins)
        set_carry(ins, carry)
        gate.call(ins, wait=True)
        fin(ins)
        for reg, reg_name in REGS_XY:
            ins = instruction(ox, oy, f"{op_name} ?{reg_name}")
            reg.is_src_j(ins)
            load_store(ins, wait=False)
            gate.call(ins, wait=True)
            set_carry(ins, carry)
            fin(ins)
        instruction(ox, oy, "")
        instruction(ox, oy, "")

    mv = GATES_1[0]
    cmp = GATES_3[2]
    test = GATES_2[2]
    for src, src_name in REGS_XYA:
        for dst, dst_name in REGS_XYA:
            if src == dst: continue
            ins = instruction(ox, oy, f"T{src_name}{dst_name}")
            dst.is_dest(ins)
            src.is_src_j(ins)
            mv.call(ins)
            fin(ins)
    instruction(ox, oy, "")
    instruction(ox, oy, "")

    for r1, r1_name in REGS_XYA:
        for r2, r2_name in REGS_XYA:
            if r1 == r2: continue
            ins = instruction(ox, oy, f"CP{r1_name}{r2_name}")
            r1.is_src_i(ins)
            r2.is_src_j(ins)
            clr_carry(ins)
            cmp.call(ins)
            fin(ins)
    ins = instruction(ox, oy, "CLC")
    clr_carry(ins)
    fin(ins)
    ins = instruction(ox, oy, "SEC")
    set_carry(ins)
    fin(ins)

    for reg, reg_name in REGS_XYA:
        ins = instruction(ox, oy, f"CP{reg_name} #")
        reg.is_src_i(ins, wait=True)
        immediate(ins)
        clr_carry(ins)
        cmp.call(ins, wait=True)
        fin(ins)
    for reg, reg_name in REGS_XYA:
        ins = instruction(ox, oy, f"CP{reg_name} ?")
        reg.is_src_i(ins, wait=True)
        load(ins)
        clr_carry(ins)
        cmp.call(ins, wait=True)
        fin(ins)
    for reg, reg_name in REGS_XY:
        ins = instruction(ox, oy, f"CPA ?{reg_name}")
        REG_A.is_src_i(ins, wait=True)
        reg.is_src_j(ins)
        load(ins, wait=False)
        cmp.call(ins, wait=True)
        fin(ins)

    for reg, reg_name in REGS_XYA:
        ins = instruction(ox, oy, f"test {reg_name}")
        reg.is_src_i(ins)
        reg.is_src_j(ins)
        clr_carry(ins)
        test.call(ins)
        fin(ins)

    for reg, reg_name in REGS_XYA:
        ins = instruction(ox, oy, f"ST{reg_name} ?")
        reg.is_src_j(ins, wait=True)
        store(ins)
        mv.call(ins, wait=True)
        fin(ins)
    for reg, reg_name in REGS_XY:
        ins = instruction(ox, oy, f"STA ?{reg_name}")
        REG_A.is_src_j(ins, wait=True)
        reg.is_src_j(ins)
        store(ins, wait=False)
        mv.call(ins, wait=True)
        fin(ins)

    for reg, reg_name in REGS_XYA:
        ins = instruction(ox, oy, f"LD{reg_name} #")
        reg.is_dest(ins, wait=True)
        immediate(ins)
        mv.call(ins, wait=True)
        fin(ins)
    for reg, reg_name in REGS_XYA:
        ins = instruction(ox, oy, f"LD{reg_name} ?")
        reg.is_dest(ins, wait=True)
        load(ins)
        mv.call(ins, wait=True)
        fin(ins)
    for reg, reg_name in REGS_XY:
        ins = instruction(ox, oy, f"LDA ?{reg_name}")
        REG_A.is_dest(ins, wait=True)
        reg.is_src_j(ins)
        load(ins, wait=False)
        mv.call(ins, wait=True)
        fin(ins)

    ins = instruction(ox, oy, "JMP")
    jump(ins)
    fin(ins)
    for reg, reg_name in REGS_XYA:
        ins = instruction(ox, oy, f"JP{reg_name}")
        reg.is_src_j(ins)
        jump(ins, wait=False)
        fin(ins)
    ins = instruction(ox, oy, "BCC")
    branch(ins, BCC)
    jump(ins)
    fin(ins)
    ins = instruction(ox, oy, "BCS")
    branch(ins, BCS)
    jump(ins)
    fin(ins)
    ins = instruction(ox, oy, "BEQ")
    branch(ins, BEQ)
    jump(ins)
    fin(ins)
    ins = instruction(ox, oy, "BNE")
    branch(ins, BNE)
    jump(ins)
    fin(ins)

#====================================================================

for i in range(N_BITS):
    step = Shape(0, w, w, w, (200, 255, 200, 0.5), z=Z(i, 1, 1))
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
ww = w
oy += (N_BITS+5)*w
BYTES = [None]*N_BYTES
for addr in range(N_BYTES):
    i = addr%R
    j = addr//R
    BYTES[addr] = Byte(ox+3*i*ww, oy+j*(N_BITS+1.5)*ww, ww, is_j=True, addr=addr)
for addr in range(N_BYTES):
    i = addr%R
    j = addr//R
    byte, next_byte = BYTES[addr], BYTES[(addr+1)%N_BYTES]
    for t in TARGETS:
        tl.add(Target(t), on=byte.ip)
    tl.add(Disappear(byte.ip), on=byte.ip)
    tl.add(Target(byte.target_j), on=byte.ip)
    tl.add(Appear(next_byte.ip), on=byte.ip)

ISA(isa_ox+4*w, isa_oy+3*w+1)

tl.add(Appear(TARGET_IMM))
tl.add(Target(TARGET_IMM))
tl.add(Target(TARGET_IP))
tl.add(Target(D_RESET))
tl.add(Target(J_RESET))
tl.add(Target(IP_RESET))
tl.add(Target(OP_RESET))
tl.add(Target(SET_0))

shapes = Shape.dump()
slide = Slide("cpu", shapes, tl)
doc = Document("cpu", [slide])
#save_to_pptx(doc)

scale = 10/Document.SCALE
tk_run(slide, Document.WIDTH*scale, Document.HEIGHT*scale, scale, smart_refresh=True, validate_exit=True)
