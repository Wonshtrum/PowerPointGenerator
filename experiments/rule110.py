from pptgen import *
from pptgen.serializer import save_to_pptx
from pptgen.runner import tk_run


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
			self.next = Shape(x, y, w, w, (255, 0, 0), z=z)
			tl.add(Disappear(self.next), on=self.next)


tl = Timeline()
n_columns = 20
n_rows = 20
n_group = 3
n_m = 1<<n_group
w = 2.5
d = 0
tx = 0
ty = 20
target = (tx, ty)


matrix = [[Shape(x*(w+1), y*(w+1), w, w, text=Text(1<<(n_group-x-1), (255, 255, 255)), z=-2-n_m) for x in range(n_group)] for y in range(n_group)]
for _ in iterate(*matrix):
	tl.add(Disappear(_), on=_)


stop = Shape(tx, ty, w, w, (0, 0, 255), z=2+n_rows)
zero = Shape(tx, ty, w, w, (120, 120, 120), z=-1-n_m)
start = Shape(tx, ty, w, w, (0, 255, 0), z=-4-n_m)
call_in = [Shape(tx, ty, w, w, (255, 0, 255), z=-3-n_m) for _ in range(n_group)]
call_out = [Shape(tx, ty, w, w, (255, 100, 255), z=-n_m) for _ in range(n_group)]
tl.add(Disappear(start), on=start)
tl.add(Disappear(zero), on=start)
tl.add(Disappear(zero), on=zero)
tl.add(Place(stop), on=stop)
for _ in iterate(call_in, call_out):
	tl.add(Disappear(_))
	tl.add(Disappear(_), on=_)
for i, o, line in zip(call_in, call_out, matrix):
	tl.add(Appear(o), on=i)
	for _ in line:
		tl.add(Place(_, target, relative=False), on=i)
		tl.add(SlideIn(_, Animation.DOWN), on=o)


controlers = []
for i in range(n_m):
	s0 = Shape((n_group+i+1)*(w+1), 0, w, w, (255, 255, 255), text=0, z=-1-n_m)
	s1 = Shape((n_group+i+1)*(w+1), 0, w, w, (255, 255, 255), text=1, z=-1-n_m)
	_ = Shape((n_group+i+1)*(w+1), w, w, w)
	controlers.append((s0, s1))
	tl.add(Disappear(s0), on=_)
	tl.add(Appear(s0, click=True), on=_)
	tl.add(Appear(zero), on=s0)
	for j in range(n_group):
		for k in range(n_group):
			if not i & 1<<(n_group-k-1):
				tl.add(Place(s0, target), on=matrix[j][k])
				tl.add(Place(s1, target), on=matrix[j][k])
for s in iterate(*controlers):
	for _ in iterate(*controlers, start):
		tl.add(Place(s), on=_)
	for _ in call_in:
		tl.add(Place(s, target, relative=False), on=_)


ox = Document.WIDTH/Document.SCALE-w
oy = 10
cells = [[None]*(n_rows) for _ in range(n_columns)]
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
				tl.add(Place(cells[x-1][y+1].reset, target, relative=False), on=cell.next)
				tl.add(Appear(call_in[x%n_group]), on=cell.next)
			for _ in [cell.main, cell.next]:
				tl.add(Place(_, target, relative=False), on=last)
			last = cell.next

	if y < n_rows-1:
		tmp = Shape(ox-(x+1)*(w+d), oy+y*(w+d), w, w, (255, 255, 0), z=1+n_rows-y)
		tl.add(Place(tmp, target, relative=False), on=last)
		tl.add(Appear(call_in[(x+i)%n_group]), on=tmp)
		tl.add(Place(cells[x][y+1].reset, target, relative=False), on=tmp)
		tl.add(Appear(cells[x][y+1].reset), on=tmp)
		tl.add(Place(tmp, click=True), on=tmp)
		last = tmp


shapes = Shape.dump()
slide = Slide("rule110", shapes, tl)
doc = Document("rule110", [slide])
#save_to_pptx(doc)
scale = 10/Document.SCALE
tk_run(slide, Document.WIDTH*scale, Document.HEIGHT*scale, scale)
