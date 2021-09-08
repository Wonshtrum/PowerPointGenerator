from document import *
from animation import *


"""
rect1 = Shape(10, 10, 10, 10, "FF0000")
rect2 = Shape(20, 20, 10, 10, "00FF00")
rect3 = Shape(30, 30, 10, 10, "0000FF")
rect4 = Shape(40, 40, 10, 10, "FFFF00")
grp1 = Group(rect1, rect2)
grp2 = Group(grp1, rect3)

tl1 = Timeline()
delay = 0
dur = 0.4
for dir in Animation.DIRECTIONS:
	tl1.add(SlideIn(rect1, dir, dur, delay, 0.5, False))
	delay += dur/2
	tl1.add(SlideOut(rect1, dir, dur, delay, 0.5, False))
	delay += dur/2

p = [(0,0), (20,0), (20,20), (0,20)]
tl2 = Timeline(SlideIn(rect4, Animation.UP, 1, 1, 0.5, False), SlideOut(rect4, Animation.LEFT, 0.5, 2, 0.5, False), Disappear(rect4), Appear(rect4, 0.5, False), Path(rect4, p, 0.2, 0, 0.5))
tl2.add(Appear(rect4, 0, False), Disappear(rect4, 1, False), Appear(rect4, 0.5), Path(rect4, p, 0.5, 0, 2.5, relative=True), on=grp2)
tl2.add(Appear(rect4, 0, True), Disappear(rect4, 1, False), Appear(rect4, 0.5), Path(rect4, p, 1, relative=True, centered=True), on=rect4)
"""

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
shapes = []
cells = []
controlers = []
ox = 20
oy = 10
for i in reversed(range(nb_symbols)):
	s = Shape(ox, oy+nb_symbols*5+i*3, 6*nb_cells-2, 2)
	controlers.append(s)
	for controler in controlers:
		tl.add(Disappear(controler, 0, False), on=s)
	shapes.append(s)

for i in range(nb_cells):
	cell = Cell()
	cell.reset = Shape(ox+i*6, oy+nb_symbols*8, 4, 4)
	cell.right = Shape(ox+i*6+2.5, oy+nb_symbols*8+5, 1.5, 1.5)
	cell.left = Shape(ox+i*6, oy+nb_symbols*8+5, 1.5, 1.5)
	for j in range(nb_symbols):
		s = Shape(ox+i*6, oy+j*5, 4, 4)
		tl.add(Disappear(s, 0, False), on=s)
		if j < nb_symbols-1:
			tl.add(Disappear(controlers[j+1], 0, False), on=s)
		cell.symbols.append(s)
	cells.append(cell)
	for s in cell.symbols:
		tl.add(Appear(s, 0, False), on=cell.reset)

for i in range(nb_cells):
	cell  = cells[i]
	right  = cells[(i+1)%nb_cells]
	left = cells[i-1]
	cells[i].save(shapes)
	for s in cell.elements():
		tl.add(Path(s, [(0, 0), (0, 0)], Animation.MIN_TIME, click=False, relative=True), on=cell.right)
		tl.add(Path(s, [(0, 0), (0, 0)], Animation.MIN_TIME, click=False, relative=True), on=cell.left)
	dx = right.reset.get_x(True)
	for s in right.elements():
		tl.add(Path(s, [(-dx, 0), (-dx, 0)], Animation.MIN_TIME, click=False, relative=True), on=cell.right)
	dx = left.reset.get_x(True)
	for s in left.elements():
		tl.add(Path(s, [(-dx, 0), (-dx, 0)], Animation.MIN_TIME, click=False, relative=True), on=cell.left)


slide = Slide("turing_machine", shapes, tl)
doc = Document("out", [slide])
doc.save()