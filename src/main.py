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
		self.left  = None
		self.reset = None
		self.cycle = None

	def elements(self):
		return iterate(self.left, self.right, self.reset, self.symbols)


tl = Timeline()
nb_symbols = 4
nb_states = 4
nb_cells = 10
cells = []
readers = []
writers = []


w  = 4
w2 = 1
ox = 20
oy = 20
master = Shape(ox, oy-w2-w*2-2, nb_cells*(w+1)-1, w, (255, 0, 0), z=-3)
read_enable = Shape(ox, oy+(nb_symbols-1)*(w+w2+1)-w2, nb_cells*(w+1)-1, w2, (255, 0, 0), z=2*nb_symbols+1)
left_enable = Shape(ox, oy+nb_symbols*(w+w2+1)-w2, nb_cells*(w+1)-1, w2, (0, 255, 0), z=2*nb_symbols+2)
tl.add(Disappear(master), on=master)
tl.add(Disappear(read_enable), on=read_enable)
tl.add(Disappear(left_enable), on=left_enable)
tl.add(Appear(read_enable), on=master)
tl.add(Appear(left_enable), on=master)

for i in reversed(range(nb_symbols)):
	s = Shape(ox, oy+(nb_symbols+1)*(w+w2+1)-w2+(w2+1)*i, nb_cells*(w+1)-1, w2, (255, 255, 0), z=2*nb_symbols+4+i)
	readers.append(s)
	for reader in readers:
		tl.add(Disappear(reader), on=s)
	tl.add(Appear(reader), on=read_enable)

for i in range(nb_symbols-1):
	s = Shape(ox, oy+i*(w+w2+1)-w2, nb_cells*(w+1)-1, w2, (0, 255, 0), z=i*2)
	tl.add(Appear(s), on=master)
	tl.add(Disappear(s), on=s)
	writers.append(s)

for i in range(nb_cells):
	cell = Cell()
	cell.reset = Shape(ox+i*(w+1), oy-w-w2-1, w, w, (255, 0, 255), z=-1)
	cell.cycle = Shape(ox+i*(w+1), oy+(nb_symbols-1)*(w+w2+1), w, w, (0, 255, 255), z=2*nb_symbols+2)
	cell.right = Shape(ox+i*(w+1)+(w-1)/2+1, oy+nb_symbols*(w+w2+1), (w-1)/2, w, z=2*nb_symbols+3)
	cell.left  = Shape(ox+i*(w+1), oy+nb_symbols*(w+w2+1), (w-1)/2, w, z=2*nb_symbols+4)

	for j in range(nb_symbols-1):
		s = Shape(ox+i*(w+1), oy+j*(w+w2+1), w, w, (0, (j+1)*255/nb_symbols, (j+1)*255/nb_symbols), z=j*2+1)
		tl.add(Disappear(s), on=s)
		tl.add(Place(s, (0, 0)), on=writers[j])
		tl.add(Disappear(readers[j+1]), on=s)
		cell.symbols.append(s)

	for s in cell.symbols:
		tl.add(Appear(s), on=cell.reset)
		tl.add(Appear(s), on=cell.cycle)

	tl.add(Appear(cell.reset), on=master)
	tl.add(Appear(cell.right), on=cell.reset)
	tl.add(Appear(cell.left), on=cell.reset)
	tl.add(Disappear(cell.reset), on=cell.reset)
	tl.add(Disappear(cell.right), on=left_enable)
	tl.add(Disappear(cell.right), on=cell.right)
	tl.add(Disappear(cell.left), on=cell.right)
	tl.add(Disappear(cell.right), on=cell.left)
	tl.add(Disappear(cell.left), on=cell.left)

	cells.append(cell)

for i in range(nb_cells):
	cell  = cells[i]
	right = cells[(i+1)%nb_cells]
	left  = cells[i-1]
	for s in cell.elements():
		tl.add(Place(s, (0, 0)), on=cell.right)
		tl.add(Place(s, (0, 0)), on=cell.left)

	tl.add(Disappear(right.reset), on=cell.right)
	tl.add(Disappear(left.reset), on=cell.left)

	dx = right.reset.get_x(True)
	for s in right.elements():
		tl.add(Place(s, (-dx, 0)), on=cell.right)
	dx = left.reset.get_x(True)
	for s in left.elements():
		tl.add(Place(s, (-dx, 0)), on=cell.left)


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
	if i != 0:
		tl.add(Place(s, (w/2, 0)))
	tl.add(Place(s, (0, 0)), on=s)
	for j in range(nb_symbols):
		other = symbol_setters[j]
		if i!=j:
			tl.add(Place(other, (w/2, 0)), on=s)
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
	tl.add(Place(s, (w/2, 0)))
	tl.add(Place(s, (0, 0)), on=s)
	for j in range(nb_states):
		other = state_setters[j]
		if i!=j:
			tl.add(Place(other, (w/2, 0)), on=s)

left  = Shape(ox, oy+(nb_symbols+nb_states+1)*(w+1), w, w)
right = Shape(ox, oy+(nb_symbols+nb_states+2)*(w+1), w, w)
tl.add(SlideIn(left_enable, Animation.UP), on=left)
tl.add(SlideIn(left_enable, Animation.UP, repeat=0.1), on=right)

tl.add(Place(right, (w/2, 0)))
tl.add(Place(right, (0, 0)), on=right)
tl.add(Place(left, (w/2, 0)), on=right)
tl.add(Place(left, (0, 0)), on=left)
tl.add(Place(right, (w/2, 0)), on=left)


w  = 2
ox = 90
oy = 10
dx = 0
dy = 30
Shape(ox-w, oy-w, (nb_states+2)*(w+1)-3, (nb_symbols+2)*(w+1)-3, (255, 0, 255))
transitions = [[None]*nb_symbols for _ in range(nb_states)]
for i in range(nb_states):
	for j in range(nb_symbols):
		t0 = Shape(ox+(w+1)*i, oy+(w+1)*j, w, w, (0, (j+1)*255/nb_symbols, (j+1)*255/nb_symbols))
		t1 = Shape(ox-dx+(w+1)*i*2, oy-dy+(w+1)*j*2, w, w, (0, 0, 255))
		transitions[i][j] = Group(t0, t1, z=-2)
for i in range(nb_states):
	for j in range(nb_symbols):
		s = transitions[i][j]
		tl.add(FadeOut(s, repeat=0.5), on=s)
		tl.add(Appear(master), on=s)
		tl.add(Appear(s), on=readers[j])
		tl.add(Disappear(s), on=master)
		for k, setter in enumerate(state_setters):
			if k == i:
				tl.add(Place(s, (dx-i*(w+1), dy-j*(w+1))), on=setter)
			else:
				tl.add(Place(s, (0, 0)), on=setter)
		for obj in iterate(writers, symbol_setters, state_setters, left_enable, left, right, *transitions):
			tl.add(SlideOut(obj, Animation.RIGHT, repeat=0.001), on=s)


tl.add(Disappear(master, click=True))
tl.add(Disappear(left_enable))
for i, reader in enumerate(readers):
	tl.add(Appear(reader))
for writer in writers:
	tl.add(Disappear(writer))
for transition in iterate(*transitions):
	tl.add(Disappear(transition))
for cell in cells:
	tl.add(Disappear(cell.cycle))
	tl.add(Disappear(cell.left))
	tl.add(Disappear(cell.right))


shapes = Shape.dump()
slide = Slide("turing_machine", shapes, tl)
doc = Document("out", [slide])
doc.save()