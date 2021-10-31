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
		self.zero = Shape(x, y, w, w, text=0)
		self.one  = Shape(x, y, w, w, text=1)
		tl.add(Appear(self.one), on=self.zero)
		tl.add(Disappear(self.zero), on=self.zero)
		tl.add(Place(self.zero), on=self.zero)
		tl.add(Place(self.one), on=self.zero)
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

		lsb = self.bits[-1]
		tl.add(Target(lsb.one), on=self.inc)
		tl.add(Target(lsb.one), on=self.dec)
		tl.add(Target(lsb.zero), on=self.inc)
		tl.add(Target(lsb.zero), on=self.dec)
		tl.add(Target(self.reset), on=self.inc)
		tl.add(Target(self.reset), on=self.dec)

	def get_controls(self):
		return [self.inc, self.dec, self.left, self.right]


class Cell:
	SYMBOLS = "+-⯇⯈[]"
	def __init__(self, x, y, w):
		self.cycle = Shape(x, y+w, w, w)
		self.symbols = [Shape(x, y, w, w, text=symbol) for i, symbol in enumerate(Cell.SYMBOLS)]
		for i, symbol in enumerate(self.symbols):
			tl.add(Appear(symbol, click=True), on=self.cycle)
			for other in self.symbols[:i]:
				tl.add(Disappear(other), on=self.cycle)


INC = 0
DEC = 1
LEFT = 2
RIGHT = 3
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


ox = 0
oy = 0
controler = Object()
controler.symbols = []
controler.reset = Shape(ox, oy, w, w, (255, 0, 0), text="R", z=-2)
tl.add(Place(controler.reset), on=controler.reset)
for i, (symbol, name) in enumerate(zip("+-⯇⯈", ("INC", "DEC", "LEFT", "RIGHT"))):
	s = Shape(ox+(i+1)*w, oy, w, w, (255, 0, 0), text=symbol, z=-2)
	tl.add(Place(s), on=s)
	setattr(controler, name, s)
	controler.symbols.append(s)


ox = 10
oy = ty
cells = [Cell(ox+x*w, oy, w) for x in range(n_cells)]
for cell in cells:
	for i in range(4):
		tl.add(Target(controler.symbols[i]), on=cell.symbols[i])

ox = 10
oy = 10
words = [Word(ox+w*i, oy, w, False) for i in range(n_words)]
for i, word in enumerate(words):
	left = words[(i-1)%n_words]
	right = words[(i+1)%n_words]
	tl.add(Appear(word.inc), on=controler.INC)
	tl.add(Appear(word.dec), on=controler.DEC)
	tl.add(Appear(word.left), on=controler.LEFT)
	tl.add(Appear(word.right), on=controler.RIGHT)
	for control in word.get_controls():
		tl.add(Target(control), on=right.left)
		tl.add(Target(control), on=left.right)
		tl.add(Target(controler.reset), on=control)
		tl.add(Disappear(control), on=controler.reset)


shapes = Shape.dump()
slide = Slide("brainfck", shapes, tl)
doc = Document("brainfck", [slide])
doc.save()