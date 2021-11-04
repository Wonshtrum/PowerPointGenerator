from pptgen import *


class Object:
	pass


def iterate(*elements):
	for element in elements:
		try:
			for sub_element in element:
				yield sub_element
		except TypeError:
			yield element


class Bit:
	def __init__(self, x, y, w, first=False):
		self.not_zero = Shape(0, y, w/2, w, (255, 0, 255), z=-4)
		self.zero = Shape(x, y, w, w, text=0)
		self.one  = Shape(x, y, w, w, text=1)

		tl.add(Appear(self.not_zero), on=self.zero)
		tl.add(Appear(self.one), on=self.zero)
		tl.add(Disappear(self.zero), on=self.zero)
		tl.add(Place(self.zero), on=self.zero)
		tl.add(Place(self.one), on=self.zero)

		tl.add(Disappear(self.not_zero), on=self.one)
		tl.add(Appear(self.zero), on=self.one)
		tl.add(Disappear(self.one), on=self.one)
		tl.add(Place(self.zero), on=self.one)
		tl.add(Place(self.one), on=self.one)

		if first:
			self.next0 = self.next1 = None
		else:
			self.next0 = Shape(x, y, w, w, text="0-", z=1)
			self.next1 = Shape(x, y, w, w, text="1+", z=1)
			tl.add(Target(self.next1), on=self.one)
			tl.add(Target(self.next0), on=self.zero)
			tl.add(Place(self.next1), on=self.next1)
			tl.add(Place(self.next0), on=self.next0)

	def link(self, other):
		tl.add(Target(other.zero), on=self.next0)
		tl.add(Target(other.one), on=self.next0)
		tl.add(Target(other.zero), on=self.next1)
		tl.add(Target(other.one), on=self.next1)


class Word:
	DEFAULT_N_BITS = 8
	def __init__(self, x, y, w, h=True):
		v = not h
		self.bits = []
		for i in range(Word.DEFAULT_N_BITS):
			bit = Bit(x+w*i*h, y+w*i*v, w)
			if i > 0:
				bit.link(self.bits[-1])
			self.bits.append(bit)

		self.inc = Shape(x+(i+1)*w*h, y+(i+1)*w*v, w, w, (0, 255, 0), text="I", z=-1)
		self.dec = Shape(x+(i+2)*w*h, y+(i+2)*w*v, w, w, (255, 0, 0), text="D", z=-1)
		self.left = Shape(x+(i+3)*w*h, y+(i+3)*w*v, w, w, (0, 0, 255), text="⯇", z=-1)
		self.right = Shape(x+(i+3)*w*h, y+(i+3)*w*v, w, w, (0, 0, 255), text="⯈", z=-1)
		self.reset = Shape(x+(i+4)*w*h, y+(i+4)*w*v, w, w, (120, 120, 120), text="R", z=-1)
		self.test = Shape(x+(i+5)*w*h, y+(i+5)*w*v, w, w, (255, 0, 255), text="T", z=-1)

		tl.add(Place(self.reset), on=self.reset)

		for control in self.get_controls():
			tl.add(Place(control), on=self.left)
			tl.add(Place(control), on=self.right)

		for bit in self.bits:
			tl.add(Place(bit.next0), on=self.reset)
			tl.add(Place(bit.next1), on=self.reset)
			tl.add(Appear(bit.next1), on=self.inc)
			tl.add(Appear(bit.next0), on=self.dec)
			tl.add(Disappear(bit.next0), on=self.inc)
			tl.add(Disappear(bit.next1), on=self.dec)
			tl.add(Target(bit.not_zero), on=self.test)

		lsb = self.bits[-1]
		tl.add(Target(lsb.one), on=self.inc)
		tl.add(Target(lsb.one), on=self.dec)
		tl.add(Target(lsb.zero), on=self.inc)
		tl.add(Target(lsb.zero), on=self.dec)
		tl.add(Target(self.reset), on=self.inc)
		tl.add(Target(self.reset), on=self.dec)

	def get_controls(self):
		return [self.inc, self.dec, self.left, self.right, self.test]


class Cell:
	SYMBOLS = "+-⯇⯈[].,"
	def __init__(self, x, y, w):
		self.cycle = Shape(x, y+w, w, w)
		self.place = Shape(x, y+w*2, w, w, (0, 0, 255), z=2)
		self.next = Shape(x, y+w*3, w, w, (255, 0, 255))
		self.skip = Shape(x, y+w*4, w, w, (255, 128, 0), text="[", z=-1)
		self.symbols = [Shape(x, y, w, w, text=symbol, z=-4*(symbol in "[]")) for i, symbol in enumerate(Cell.SYMBOLS)]
		self.stack = [(
			Shape(x, y-w*(i+1), w/2, w, (255, 255*(i==n_stack-1), 255), text="▲"),
			Shape(x+w/2, y-w*(i+1), w/2, w, (255, 255*(i==0), 255), text="▼")) for i in range(n_stack)]

		for i, symbol in enumerate(self.symbols):
			tl.add(Appear(symbol, click=True), on=self.cycle)
			tl.add(Target(symbol), on=self.place)
			if i > 0:
				tl.add(Disappear(self.symbols[i-1]), on=self.cycle)

		for i, (up, down) in enumerate(self.stack):
			if i < n_stack-1:
				next_up, next_down = self.stack[i+1]
				tl.add(Appear(next_up), on=up)
				tl.add(Appear(next_down), on=up)
				tl.add(Place(next_up), on=up)
				tl.add(Place(next_down), on=up)
				tl.add(Disappear(up), on=up)
				tl.add(Disappear(down), on=up)
			if i > 0:
				prev_up, prev_down = self.stack[i-1]
				tl.add(Appear(prev_up), on=down)
				tl.add(Appear(prev_down), on=down)
				tl.add(Place(prev_up), on=down)
				tl.add(Place(prev_down), on=down)
				tl.add(Disappear(up), on=down)
				tl.add(Disappear(down), on=down)

		tl.add(Target(self.stack[0][0]), on=self.symbols[PUSH])
		tl.add(Target(self.skip), on=self.symbols[PUSH])
		tl.add(Target(self.next), on=self.stack[1][1])
		tl.add(Target(self.place), on=self.next)
		tl.add(Disappear(self.skip), on=self.next)

		tl.add(Place(self.place), on=self.place)
		tl.add(Place(self.next), on=self.next)
		tl.add(Place(self.skip), on=self.skip)


class Character:
	SYMBOLS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	def __init__(self, x, y, w, controler):
		self.symbols = [Shape(x, y, w, w, text=symbol) for i, symbol in enumerate(Character.SYMBOLS)]
		self.save = Shape(x, y+w, w, w, (0, 255, 0))
		self.reveal = Shape(tx, ty, w, w, (128, 128, 128), z=3)
		for i, symbol in enumerate(self.symbols):
			tl.add(SlideOut(symbol, Animation.UP, repeat=0.001), on=self.save)
			for j, bit in enumerate(controler):
				if not i & (1<<j):
					tl.add(Place(symbol, (0, -w)), on=bit)
			tl.add(Place(symbol, (0, 0), relative=False), on=self.reveal)
			tl.add(Appear(self.save), on=self.reveal)
			tl.add(Target(self.save), on=self.reveal)
			tl.add(Disappear(self.reveal), on=self.reveal)


INC = 0
DEC = 1
LEFT = 2
RIGHT = 3
PUSH = 4
POP = 5
OUT = 6
IN = 7

n_cells = 10
n_words = 5
n_chars = 5
n_bits  = 6
n_stack = 3

n_stack += 1

Word.DEFAULT_N_BITS = n_bits
Text.DEFAULT_COLOR = (255, 255, 255)
Text.DEFAULT_SIZE = 14
tl = Timeline()
Target = lambda s: Place(s, target, relative=False)


w = 2
tx = 0
ty = 50
target = (tx, ty)
start = Shape(tx, ty, w, w, (0, 255, 0), text="S", z=-5)
end = Shape(tx, ty, w, w, (128, 128, 128), text="■", z=4)
tl.add(Place(end), on=end)


ox = 10
oy = ty
cells = [Cell(ox+x*w, oy, w) for x in range(n_cells)]
ox = 10
oy = 10
words = [Word(ox+w*i, oy, w, False) for i in range(n_words)]
ox = 50
oy = 10
char_controler = [Shape(ox+w*i, oy+2*w, w, w, (255, 255, 0), z=-4) for i in range(n_bits)]
chars = [Character(ox+w*i, oy, w, char_controler) for i in range(n_chars)]


ox = 0
oy = 0
controler = Object()
controler.symbols = []
for i, (symbol, name) in enumerate(zip(Cell.SYMBOLS, ("INC", "DEC", "LEFT", "RIGHT", "PUSH", "POP", "OUT", "IN"))):
	s = Shape(ox+i*w, oy, w, w, (255, 0, 0), text=symbol, z=-3)
	setattr(controler, name, s)
	controler.symbols.append(s)
controler.RESET = Shape(ox+(i+1)*w+1, oy, w, w, (255, 0, 0), text="R", z=-3)
controler.LOOP  = Shape(ox+(i+2)*w+2, oy, w, w, (255, 0, 0), text="L", z=-3)
controler.SKIP  = Shape(ox+(i+3)*w+3, oy, w, w, (255, 128, 0), text="S", z=-3)
controler.COVER = Shape(ox+(i+4)*w+3, oy, w, w, (255, 128, 0), text="C", z=-3)
controler.RESET_COVER = Shape(ox+(i+5)*w+3, oy, w, w, (255, 128, 0), text="R", z=-3)
controler.COVERS = [(
	Shape(ox+(i+5+j)*w+3+w/2, oy, w/2, w, (255, 128, 0), text="▲", z=-3, ignore=j==n_stack-1),
	Shape(ox+(i+5+j)*w+3, oy, w/2, w, (255, 128, 0), text="▼", z=-3, ignore=j==0)) for j in range(n_stack-1, -1, -1)][::-1]

for i, (up, down) in enumerate(controler.COVERS):
	if i < n_stack-1:
		next_up, next_down = controler.COVERS[i+1]
		if i < n_stack-2:
			tl.add(Appear(next_up), on=up)
			tl.add(Place(next_up), on=up)
		tl.add(Appear(next_down), on=up)
		tl.add(Place(next_down), on=up)
		tl.add(Disappear(up), on=up)
		if i > 0:
			tl.add(Disappear(down), on=up)
	if i > 0:
		prev_up, prev_down = controler.COVERS[i-1]
		tl.add(Appear(prev_up), on=down)
		if i > 1:
			tl.add(Appear(prev_down), on=down)
			tl.add(Place(prev_down), on=down)
		tl.add(Place(prev_up), on=down)
		if i < n_stack-1:
			tl.add(Disappear(up), on=down)
		tl.add(Disappear(down), on=down)
for i, (up, down) in enumerate(controler.COVERS):
	if i < n_stack-1:
		tl.add(Target(up), on=controler.SKIP)
	if i > 0:
		tl.add(Target(down), on=controler.POP)
		if i < n_stack-1:
			tl.add(Target(controler.RESET_COVER), on=up)
		if i > 1:
			tl.add(Target(controler.RESET_COVER), on=down)

tl.add(Place(controler.RESET), on=controler.RESET)
tl.add(Place(controler.LOOP), on=controler.LOOP)
tl.add(Place(controler.RESET_COVER), on=controler.RESET_COVER)
tl.add(Place(controler.SKIP), on=controler.SKIP)
tl.add(Place(controler.COVER), on=controler.COVER)
tl.add(Target(controler.RESET), on=controler.RESET_COVER)
tl.add(Appear(controler.COVER), on=controler.COVERS[0][0])
tl.add(Disappear(controler.COVER), on=controler.COVERS[1][1])


for i, char in enumerate(chars):
	if i > 0:
		prev = chars[i-1]
		tl.add(Appear(char.save), on=prev.save)
		tl.add(Place(char.save), on=prev.save)
	tl.add(Disappear(char.save), on=char.save)
	tl.add(Target(char.save), on=controler.OUT)
	for symbol in char.symbols:
		tl.add(Place(symbol), on=controler.OUT)
for bit in char_controler:
	tl.add(Appear(bit), on=controler.OUT)
	tl.add(Place(bit), on=bit)
	tl.add(Place(controler.LOOP), on=bit)
	tl.add(Disappear(bit), on=controler.RESET)
	tl.add(Place(bit), on=controler.RESET)


for i, cell in enumerate(cells):
	for symbol in cell.symbols:
		tl.add(Place(symbol), on=symbol)
		tl.add(Place(symbol), on=controler.COVER)
	tl.add(Place(controler.COVER), on=cell.symbols[PUSH])
	tl.add(Place(controler.COVER), on=cell.symbols[POP])
	for j, (up, down) in enumerate(cell.stack):
		if j > 0:
			tl.add(Target(up), on=controler.PUSH)
			tl.add(Target(down), on=controler.POP)
			tl.add(Place(down), on=controler.RESET_COVER)
		tl.add(Place(up), on=controler.RESET_COVER)
	for j in range(len(Cell.SYMBOLS)):
		tl.add(Target(controler.symbols[j]), on=cell.symbols[j])
	tl.add(Target(controler.SKIP), on=cell.skip)
	if i+1 < n_cells:
		right = cells[i+1]
		tl.add(Target(right.place), on=cell.place)
		tl.add(Place(right.place), on=controler.LOOP)
		tl.add(Appear(cell.skip), on=right.place)
		tl.add(Place(cell.skip), on=right.place)
		tl.add(Target(controler.COVER), on=right.place)
	tl.add(Appear(cell.next), on=controler.LOOP)
	tl.add(Place(cell.next), on=controler.LOOP)
	tl.add(Disappear(cell.next), on=controler.POP)
for s in controler.symbols:
	tl.add(Place(s), on=s)


for i, word in enumerate(words):
	left = words[(i-1)%n_words]
	right = words[(i+1)%n_words]
	tl.add(Appear(word.inc), on=controler.INC)
	tl.add(Appear(word.dec), on=controler.DEC)
	tl.add(Appear(word.left), on=controler.LEFT)
	tl.add(Appear(word.right), on=controler.RIGHT)
	tl.add(Appear(word.test), on=controler.POP)
	tl.add(Appear(word.test), on=controler.OUT)
	for control in word.get_controls():
		tl.add(Target(control), on=right.left)
		tl.add(Target(control), on=left.right)
		tl.add(Target(controler.RESET), on=control)
		tl.add(Disappear(control), on=controler.RESET)

	for bit, char_bit in zip(word.bits, char_controler[::-1]):
		tl.add(Target(controler.LOOP), on=bit.not_zero)
		tl.add(Place(bit.not_zero), on=bit.not_zero)
		tl.add(Place(bit.not_zero), on=controler.RESET)
		tl.add(Target(char_bit), on=bit.not_zero)
		tl.add(Disappear(bit.next0), on=start)
		tl.add(Disappear(bit.next1), on=start)


tl.add(Disappear(start), on=start)
tl.add(Target(words[-1].right), on=start)
tl.add(Target(cells[0].place), on=start)


shapes = Shape.dump()
slide = Slide("brainfck", shapes, tl)
doc = Document("brainfck", [slide])
doc.save()