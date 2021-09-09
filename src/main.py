from document import *
from animation import *


class Cell:
	def __init__(self):
		self.symbols = []
		self.right = None
		self.left = None
		self.reset = None

	def elements(self):
		yield self.left
		yield self.reset
		yield self.right
		for s in self.symbols:
			yield s

	def save(self, shapes):
		shapes.extend(self.elements())


tl = Timeline()
nb_symbols = 4
nb_cells = 16
ox = 20
oy = 10
shapes = []
cells = []
readers = []
writers = []

master = Shape(ox, oy-6, nb_cells*4-1, 3)
read_enable = Shape(ox, oy+(nb_symbols-1)*6-2, nb_cells*4-1, 1)
tl.add(Disappear(master), on=master)
tl.add(Disappear(read_enable), on=read_enable)
tl.add(Appear(read_enable), on=master)
shapes.append(master)
shapes.append(read_enable)

for i in reversed(range(nb_symbols)):
	s = Shape(ox, oy+nb_symbols*6+i*3, nb_cells*4-1, 2)
	readers.append(s)
	for reader in readers:
		tl.add(Disappear(reader), on=s)
	tl.add(Appear(reader), on=read_enable)
	shapes.append(s)

for i in range(nb_symbols-1):
	s = Shape(ox, oy+i*6-2, nb_cells*4-1, 1)
	tl.add(Appear(s), on=master)
	tl.add(Disappear(s), on=s)
	writers.append(s)
	shapes.append(s)

for i in range(nb_cells):
	cell = Cell()
	cell.reset = Shape(ox+i*4, oy+nb_symbols*9, 3, 3)
	cell.right = Shape(ox+i*4+2, oy+nb_symbols*6-2, 1, 1)
	cell.left = Shape(ox+i*4, oy+nb_symbols*6-2, 1, 1)

	for j in range(nb_symbols-1):
		s = Shape(ox+i*4, oy+j*6, 3, 3)
		tl.add(Disappear(s), on=s)
		tl.add(SlideOut(s, Animation.DOWN, 1, repeat=0.8), on=writers[j])
		tl.add(Disappear(readers[j+1]), on=s)
		cell.symbols.append(s)

	for s in cell.symbols:
		tl.add(Appear(s), on=cell.reset)

	tl.add(Appear(master), on=cell.reset)
	tl.add(Disappear(cell.right))
	tl.add(Disappear(cell.left))
	tl.add(Appear(cell.right), on=cell.reset)
	tl.add(Appear(cell.left), on=cell.reset)
	tl.add(Disappear(cell.right), on=cell.right)
	tl.add(Disappear(cell.left), on=cell.right)
	tl.add(Disappear(cell.right), on=cell.left)
	tl.add(Disappear(cell.left), on=cell.left)

	cells.append(cell)
	cell.save(shapes)

for i in range(nb_cells):
	cell  = cells[i]
	right  = cells[(i+1)%nb_cells]
	left = cells[i-1]
	for s in cell.elements():
		tl.add(Path(s, [(0, 0), (0, 0)], Animation.MIN_TIME, relative=True), on=cell.right)
		tl.add(Path(s, [(0, 0), (0, 0)], Animation.MIN_TIME, relative=True), on=cell.left)

	dx = right.reset.get_x(True)
	for s in right.elements():
		tl.add(Path(s, [(-dx, 0), (-dx, 0)], Animation.MIN_TIME, relative=True), on=cell.right)
	dx = left.reset.get_x(True)
	for s in left.elements():
		tl.add(Path(s, [(-dx, 0), (-dx, 0)], Animation.MIN_TIME, relative=True), on=cell.left)


slide = Slide("turing_machine", shapes, tl)
doc = Document("out", [slide])
doc.save()