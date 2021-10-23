from pptgen import *


def iterate(*elements):
	for element in elements:
		try:
			for sub_element in element:
				yield sub_element
		except TypeError:
			yield element


class Cell:
	def __init__(self, x, y, w, z=1, first=False, last=False):
		self.main = Shape(x, y, w, w, z=z)
		self.reset = Shape(x, y-w*first, w, w, (0, 255, 255), z=z)
		tl.add(Appear(self.main), on=self.reset)
		tl.add(Place(self.main), on=self.main)
		if not last:
			self.next = Shape(x, y-w*first, w, w, (255, 0, 0), z=z)
			tl.add(Disappear(self.next), on=self.next)


	def __iter__(self):
		return iter((self.main, self.reset, self.next))


tl = Timeline()
n_columns = 5
n_rows = 5
n_group = 3
w = 2.5
d = 0


matrix = [[Shape(x*(w+1), y*(w+1), w, w, text=Text(1<<(n_group-x-1), (255, 255, 255)), z=-1<<n_group) for x in range(n_group)] for y in range(n_group)]
for _ in iterate(*matrix):
	tl.add(Disappear(_), on=_)

start = Shape(0, 20, w, w, (0, 255, 0), z=-1-1<<n_group)
zero = Shape(0, 20, w, w, (120, 120, 120), z=-1<<n_group)
tl.add(Disappear(start), on=start)
tl.add(Disappear(zero), on=start)
tl.add(Disappear(zero), on=zero)

controlers = []
for i in range(1<<n_group):
	s0 = Shape((n_group+i+1)*(w+1), 0, w, w, (0, 0, 255), text=0)
	s1 = Shape((n_group+i+1)*(w+1), 0, w, w, (0, 0, 255), text=1)
	_ = Shape((n_group+i+1)*(w+1), w, w, w)
	controlers.append((s0, s1))
	tl.add(Place(s0), on=s0)
	tl.add(Disappear(s0), on=_)
	tl.add(Appear(s0, click=True), on=_)
	tl.add(Appear(zero), on=s0)


states = []
for y in range(n_group):
	state = []
	for x in range(1<<n_group):
		s = Shape(0, 20, w, w, (255, 0, 255), text=x, z=-x)
		state.append(s)
		tl.add(Disappear(s))
		tl.add(Place(controlers[x][0], (0, 20), relative=False), on=s)
		for i in range(n_group):
			if x & 1<<i:
				tl.add(Disappear(s), on=matrix[y][n_group-i-1])
	for i, s in enumerate(state):
		for _ in state[:i+1]:
			tl.add(Disappear(_), on=s)
		for _ in matrix[y]:
			tl.add(SlideIn(_, Animation.DOWN), on=s)
	states.append(state)



cells = [[None]*(n_rows) for _ in range(n_columns)]
ox = Document.WIDTH/Document.SCALE-w
oy = 10

for y in range(n_rows):
	for x in range(n_columns):
		cells[x][y] = Cell(ox-x*(w+d), oy+y*(w+d), w, 1+n_rows-y, y==0, y==n_rows-1)


last = start
for y in range(n_rows):
	for _ in iterate(*matrix):
		tl.add(Appear(_), on=last)
	for x in range(n_columns):
		cell = cells[x][y]
		tl.add(Disappear(cell.main))
		if x > 0:
			tl.add(Disappear(matrix[(x+0)%n_group][0]), on=cell.main)
		tl.add(Disappear(matrix[(x+1)%n_group][1]), on=cell.main)
		tl.add(Disappear(matrix[(x+2)%n_group][2]), on=cell.main)
		if y == 0:
			tl.add(Disappear(cell.main, click=True), on=cell.reset)
		else:
			tl.add(Disappear(cell.reset), on=cell.reset)
			tl.add(Disappear(cell.reset), on=zero)
		if y < n_rows-1:
			if x > 0:
				tl.add(Appear(cells[x-1][y+1].reset), on=cell.next)
				tl.add(Place(cells[x-1][y+1].reset, (0, 20), relative=False), on=cell.next)
				for _ in matrix[x%n_group]:
					tl.add(Place(_, (0, 20), relative=False), on=cell.next)
				for _ in states[x%n_group]:
					tl.add(Appear(_), on=cell.next)
			for _ in [cell.main, cell.next]:
				tl.add(Place(_, (0, 20), relative=False), on=last)
			last = cell.next

	if y < n_rows-1:
		tmp = Shape(ox-(x+1)*(w+d), oy+y*(w+d), w, w, (255, 255, 0), z=1+n_rows-y)
		tl.add(Place(tmp, (0, 20), relative=False), on=last)
		for _ in matrix[(x+i)%n_group]:
			tl.add(Place(_, (0, 20), relative=False), on=tmp)
		for _ in states[(x+i)%n_group]:
			tl.add(Appear(_), on=tmp)
		tl.add(Place(cells[x][y+1].reset, (0, 20), relative=False), on=tmp)
		tl.add(Appear(cells[x][y+1].reset), on=tmp)
		tl.add(Place(tmp, click=True), on=tmp)
		last = tmp


shapes = Shape.dump()
slide = Slide("rule110", shapes, tl)
doc = Document("rule110", [slide])
doc.save()