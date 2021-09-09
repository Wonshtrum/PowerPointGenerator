from document import *
from animation import *


def iterate(*elements):
	for element in elements:
		try:
			for sub_element in element:
				yield sub_element
		except TypeError:
			yield element


class Cell:
	def __init__(self):
		self.symbols = []
		self.right = None
		self.left = None
		self.reset = None

	def elements(self):
		return iterate(self.left, self.right, self.reset, self.symbols)


tl = Timeline()
nb_symbols = 4
nb_states = 4
nb_cells = 16
ox = 20
oy = 10
cells = []
readers = []
writers = []

master = Shape(ox, oy-6, nb_cells*4-1, 3)
read_enable = Shape(ox, oy+(nb_symbols-1)*6-2, nb_cells*4-1, 1)
left_enable = Shape(ox, oy+nb_symbols*6-4, nb_cells*4-1, 1)
tl.add(Disappear(master), on=master)
tl.add(Disappear(read_enable), on=read_enable)
tl.add(Disappear(left_enable), on=left_enable)
tl.add(Appear(read_enable), on=master)
tl.add(Appear(left_enable), on=master)

for i in reversed(range(nb_symbols)):
	s = Shape(ox, oy+nb_symbols*6+i*3, nb_cells*4-1, 2)
	readers.append(s)
	for reader in readers:
		tl.add(Disappear(reader), on=s)
	tl.add(Appear(reader), on=read_enable)
	tl.add(Appear(master), on=s)
	tl.add(Appear(reader))

for i in range(nb_symbols-1):
	s = Shape(ox, oy+i*6-2, nb_cells*4-1, 1)
	tl.add(Appear(s), on=master)
	tl.add(Disappear(s), on=s)
	writers.append(s)

for i in range(nb_cells):
	cell = Cell()
	cell.reset = Shape(ox+i*4, oy+nb_symbols*9, 3, 3)
	cell.right = Shape(ox+i*4+2, oy+nb_symbols*6-2, 1, 1)
	cell.left = Shape(ox+i*4, oy+nb_symbols*6-2, 1, 1)

	for j in range(nb_symbols-1):
		s = Shape(ox+i*4, oy+j*6, 3, 3)
		tl.add(Disappear(s), on=s)
		tl.add(SlideOut(s, Animation.DOWN, repeat=0.8), on=writers[j])
		tl.add(Disappear(readers[j+1]), on=s)
		cell.symbols.append(s)

	for s in cell.symbols:
		tl.add(Appear(s), on=cell.reset)

	tl.add(Appear(cell.reset), on=master)
	tl.add(Appear(cell.right), on=cell.reset)
	tl.add(Appear(cell.left), on=cell.reset)
	tl.add(Disappear(cell.reset), on=cell.reset)
	tl.add(Disappear(cell.right), on=left_enable)
	tl.add(Disappear(cell.right))
	tl.add(Disappear(cell.left))
	tl.add(Disappear(cell.right), on=cell.right)
	tl.add(Disappear(cell.left), on=cell.right)
	tl.add(Disappear(cell.right), on=cell.left)
	tl.add(Disappear(cell.left), on=cell.left)

	cells.append(cell)

for i in range(nb_cells):
	cell  = cells[i]
	right  = cells[(i+1)%nb_cells]
	left = cells[i-1]
	for s in cell.elements():
		tl.add(Path(s, [(0, 0), (0, 0)], relative=True), on=cell.right)
		tl.add(Path(s, [(0, 0), (0, 0)], relative=True), on=cell.left)

	tl.add(Disappear(right.reset), on=cell.right)
	tl.add(Disappear(left.reset), on=cell.left)

	dx = right.reset.get_x(True)
	for s in right.elements():
		tl.add(Path(s, [(-dx, 0), (-dx, 0)], relative=True), on=cell.right)
	dx = left.reset.get_x(True)
	for s in left.elements():
		tl.add(Path(s, [(-dx, 0), (-dx, 0)], relative=True), on=cell.left)

w  = 4
ox = Document.WIDTH/Document.SCALE-w
oy = 1
symbol_setters = []
state_setters = []

for i in range(nb_symbols):
	s = Shape(ox, oy+i*(w+1), w, w)
	symbol_setters.append(s)
for i in range(nb_symbols):
	s = symbol_setters[i]
	tl.add(SlideIn(s, Animation.LEFT, repeat=0.5))
	tl.add(SlideIn(s, Animation.LEFT), on=s)
	for j in range(nb_symbols):
		other = symbol_setters[j]
		if i!=j:
			tl.add(SlideIn(other, Animation.LEFT, repeat=0.5), on=s)
	for j, writer in enumerate(writers):
		if j >= i:
			tl.add(SlideIn(writer, Animation.UP), on=s)
		else:
			tl.add(SlideIn(writer, Animation.UP, repeat=0.1), on=s)

for i in range(nb_states):
	s = Shape(ox, oy+(nb_symbols+i+0.5)*(w+1), w, w)
	state_setters.append(s)
for i in range(nb_states):
	s = state_setters[i]
	tl.add(SlideIn(s, Animation.LEFT, repeat=0.5))
	tl.add(SlideIn(s, Animation.LEFT), on=s)
	for j in range(nb_states):
		other = state_setters[j]
		if i!=j:
			tl.add(SlideIn(other, Animation.LEFT, repeat=0.5), on=s)

right = Shape(ox, oy+(nb_symbols+nb_states+1)*(w+1), w, w)
left  = Shape(ox, oy+(nb_symbols+nb_states+2)*(w+1), w, w)
tl.add(SlideIn(left_enable, Animation.UP), on=left)
tl.add(SlideIn(left_enable, Animation.UP, repeat=0.1), on=right)

tl.add(SlideIn(right, Animation.LEFT, repeat=0.5))
tl.add(SlideIn(right, Animation.LEFT), on=right)
tl.add(SlideIn(right, Animation.LEFT, repeat=0.5), on=left)

tl.add(SlideIn(left, Animation.LEFT, repeat=0.5))
tl.add(SlideIn(left, Animation.LEFT), on=left)
tl.add(SlideIn(left, Animation.LEFT, repeat=0.5), on=right)

ox = 90
oy = 10
w  = 2
next_transition = Shape(ox-w, oy-w, (nb_states+2)*(w+1)-3, (nb_symbols+2)*(w+1)-3, "FF00FF")
transitions = [[None]*nb_symbols for _ in range(nb_states)]
for i in range(nb_states):
	for j in range(nb_symbols):
		transitions[i][j] = Shape(ox+(w+1)*i, oy+(w+1)*j, w, w)
for i in range(nb_states):
	for j in range(nb_symbols):
		s = transitions[i][j]
		tl.add(FadeOut(s, repeat=0.5), on=s)
		tl.add(Appear(s), on=readers[j])
		tl.add(Appear(s), on=next_transition)
		for transition in iterate(*transitions):
			tl.add(Disappear(transition), on=s)
		for k, setter in enumerate(state_setters):
			if k == i:
				tl.add(Path(s, [(0, 20), (0, 20)], relative=True), on=setter)
			else:
				tl.add(Path(s, [(0, 0), (0, 0)], relative=True), on=setter)
		for obj in iterate(writers, symbol_setters, state_setters, left_enable, left, right, *transitions):
			tl.add(SlideOut(obj, Animation.RIGHT, repeat=0.001), on=s)


shapes = Shape.dump()
slide = Slide("turing_machine", shapes, tl)
doc = Document("out", [slide])
doc.save()