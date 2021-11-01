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
		self.not_zero = Shape(x, y, w/2, w, (255, 0, 255), z=-2)
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
	SYMBOLS = "+-⯇⯈[]"
	def __init__(self, x, y, w):
		self.cycle = Shape(x, y+w, w, w)
		self.place = Shape(x, y+w*2, w, w, (0, 0, 255), z=2)
		self.next = Shape(x, y+w*3, w, w, (255, 0, 255))
		self.symbols = [Shape(x, y, w, w, text=symbol) for i, symbol in enumerate(Cell.SYMBOLS)]
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
		tl.add(Target(self.next), on=self.stack[1][1])
		tl.add(Target(self.place), on=self.next)

		tl.add(Place(self.place), on=self.place)
		tl.add(Place(self.next), on=self.next)


INC = 0
DEC = 1
LEFT = 2
RIGHT = 3
PUSH = 4
POP = 5
Word.DEFAULT_N_BITS = 4
Text.DEFAULT_COLOR = (255, 255, 255)
tl = Timeline()
Target = lambda s: Place(s, target, relative=False)

w = 3
tx = 0
ty = 50
target = (tx, ty)

n_cells = 10
n_words = 10
n_stack = 3
n_stack += 1


start = Shape(tx, ty, w, w, (0, 255, 0), text="S", z=-4)
ox = 10
oy = ty
cells = [Cell(ox+x*w, oy, w) for x in range(n_cells)]
ox = 10
oy = 10
words = [Word(ox+w*i, oy, w, False) for i in range(n_words)]


ox = 0
oy = 0
controler = Object()
controler.symbols = []
for i, (symbol, name) in enumerate(zip("+-⯇⯈[]", ("INC", "DEC", "LEFT", "RIGHT", "PUSH", "POP"))):
	s = Shape(ox+i*w, oy, w, w, (255, 0, 0), text=symbol, z=-3)
	setattr(controler, name, s)
	controler.symbols.append(s)
controler.RESET = Shape(ox+(i+1)*w+1, oy, w, w, (255, 0, 0), text="R", z=-3)
controler.LOOP  = Shape(ox+(i+2)*w+2, oy, w, w, (255, 0, 0), text="L", z=-3)
tl.add(Place(controler.RESET), on=controler.RESET)
tl.add(Place(controler.LOOP), on=controler.LOOP)


ox = 10
oy = ty
for i, cell in enumerate(cells):
	for symbol in cell.symbols:
		tl.add(Place(symbol), on=symbol)
	for up, down in cell.stack[1:]:
		tl.add(Target(up), on=controler.PUSH)
		tl.add(Target(down), on=controler.POP)
	for j in range(6):
		tl.add(Target(controler.symbols[j]), on=cell.symbols[j])
	if i+1 < n_cells:
		right = cells[i+1]
		tl.add(Target(right.place), on=cell.place)
		tl.add(Place(right.place), on=controler.LOOP)
	tl.add(Appear(cell.next), on=controler.LOOP)
	tl.add(Place(cell.next), on=controler.LOOP)
	tl.add(Disappear(cell.next), on=controler.POP)
for s in controler.symbols:
	tl.add(Place(s), on=s)


ox = 10
oy = 10
for i, word in enumerate(words):
	left = words[(i-1)%n_words]
	right = words[(i+1)%n_words]
	tl.add(Appear(word.inc), on=controler.INC)
	tl.add(Appear(word.dec), on=controler.DEC)
	tl.add(Appear(word.left), on=controler.LEFT)
	tl.add(Appear(word.right), on=controler.RIGHT)
	tl.add(Appear(word.test), on=controler.POP)
	for control in word.get_controls():
		tl.add(Target(control), on=right.left)
		tl.add(Target(control), on=left.right)
		tl.add(Target(controler.RESET), on=control)
		tl.add(Disappear(control), on=controler.RESET)

	for bit in word.bits:
		tl.add(Target(controler.LOOP), on=bit.not_zero)
		tl.add(Place(bit.not_zero), on=controler.LOOP)
		tl.add(Disappear(bit.next0), on=start)
		tl.add(Disappear(bit.next1), on=start)


tl.add(Disappear(start), on=start)
tl.add(Target(words[-1].right), on=start)
tl.add(Target(cells[0].place), on=start)


shapes = Shape.dump()
slide = Slide("brainfck", shapes, tl)
doc = Document("brainfck", [slide])
doc.save()