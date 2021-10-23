from pptgen import *


def iterate(*elements):
	for element in elements:
		try:
			for sub_element in element:
				yield sub_element
		except TypeError:
			yield element


class Cell:
	def __init__(self, x, y, w, z=1, first=False):
		self.main = Shape(x, y, w, w, z=z)
		self.reset = Shape(x, y-w*first, w, w, (0, 255, 255), z=z)
		self.next = Shape(x, y-w*first, w, w, (255, 0, 0), z=z)

	def __iter__(self):
		return iter((self.main, self.reset, self.next))


tl = Timeline()
n_columns = 10
n_rows = 10
n_group = 3

w = 3
matrix = [[Shape(x*(w+1), y*(w+1), w, w, text=Text(1<<(n_group-x-1), (255, 255, 255)), z=-1<<n_group) for x in range(n_group)] for y in range(n_group)]
for _ in iterate(*matrix):
	tl.add(Disappear(_), on=_)

controlers = []
for i in range(1<<n_group):
	s = Shape((n_group+i+1)*(w+1), 0, w, w, (0, 0, 255))
	_ = Shape((n_group+i+1)*(w+1), w, w, w)
	controlers.append(s)
	tl.add(Place(s), on=s)
	tl.add(Disappear(s), on=_)
	tl.add(Appear(s, click=True), on=_)

states = []
for y in range(n_group):
	state = []
	for x in range(1<<n_group):
		s = Shape(0, 20, w, w, (255, 0, 255), text=x, z=-x)
		state.append(s)
		tl.add(Disappear(s))
		tl.add(Place(controlers[x], (0, 20), relative=False), on=s)
		for i in range(n_group):
			if x & 1<<i:
				tl.add(Disappear(s), on=matrix[y][n_group-i-1])
	for i, s in enumerate(state):
		for _ in state[:i+1]:
			tl.add(Disappear(_), on=s)
		for _ in matrix[y]:
			tl.add(SlideIn(_, Animation.DOWN), on=s)
	states.append(state)

start = Shape(0, 20.5, w, w, (0, 255, 0), z=-1<<n_group)
tl.add(Disappear(start), on=start)


w = 3
d = 0.5
cells = [[None]*n_columns for _ in range(n_rows)]
ox = Document.WIDTH/Document.SCALE-w
oy = 10
last = start
for y in range(n_rows):
	for _ in iterate(*matrix):
		tl.add(Appear(_), on=last)
	for x in range(n_columns):
		cell = Cell(ox-x*(w+d), oy+y*(w+d), w, 1+n_rows-y, y==0)
		cells[x][y] = cell
		tl.add(Disappear(matrix[(x+0)%n_group][0]), on=cell.main)
		tl.add(Disappear(matrix[(x+1)%n_group][1]), on=cell.main)
		tl.add(Disappear(matrix[(x+2)%n_group][2]), on=cell.main)
		tl.add(Disappear(cell.next), on=cell.next)
		tl.add(Appear(cell.main), on=cell.reset)
		tl.add(Place(cell.main), on=cell.main)
		if y == 0:
			tl.add(Disappear(cell.main, click=True), on=cell.reset)
		else:
			tl.add(Disappear(cell.reset), on=cell.reset)
			for _ in controlers:
				tl.add(Disappear(cell.reset), on=_)
		for _ in matrix[x%n_group]:
			tl.add(Place(_, (0, 20), relative=False), on=cell.next)
		for _ in states[x%n_group]:
			tl.add(Appear(_), on=cell.next)
		for _ in [cell.main, cell.next]:
			tl.add(Place(_, (0, 20), relative=False), on=last)
		last = cell.next

for y in range(n_rows):
	for x in range(n_columns):
		tl.add(Disappear(cells[x][y].main))
		if y > 0:
			tl.add(Place(cells[x][y].reset, (0, 20), relative=False), on=cells[x][y-1].next)
			tl.add(Appear(cells[x][y].reset), on=cells[x][y-1].next)


shapes = Shape.dump()
slide = Slide("rule110", shapes, tl)
doc = Document("rule110", [slide])
doc.save()