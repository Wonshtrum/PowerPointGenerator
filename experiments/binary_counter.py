from pptgen import *


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
	def __init__(self, x, y, w, h=True):
		v = not h
		self.bits = []
		for i in range(5):
			bit = Bit(x+w*i*h, y+w*i*v, w)
			if i > 0:
				bit.link(self.bits[-1])
			self.bits.append(bit)

		self.inc = Shape(x+(i+1)*w*h, y+(i+1)*w*v, w, w, (0, 255, 0), text="I", z=-1)
		self.dec = Shape(x+(i+2)*w*h, y+(i+2)*w*v, w, w, (255, 0, 0), text="D", z=-1)
		self.reset = Shape(x+(i+2)*w*h, y+(i+2)*w*v, w, w, (120, 120, 120), text="R", z=-1)
		tl.add(Place(self.reset), on=self.reset)

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


tl = Timeline()
Text.DEFAULT_COLOR = (255, 255, 255)
Target = lambda s: Place(s, target, relative=False)

tx = 0
ty = 10
target = (tx, ty)

ox = 10
oy = 10
w = 3
d = 1
for i in range(16):
	Word(ox+(w+d)*i, oy, w, False)


shapes = Shape.dump()
slide = Slide("binary", shapes, tl)
doc = Document("binary", [slide])
doc.save()