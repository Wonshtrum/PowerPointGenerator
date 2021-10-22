from pptgen import *


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

	def get_x(self, scale=True):
		return self.reset.get_x(scale)
	def get_y(self, scale=True):
		return self.reset.get_y(scale)

	def elements(self):
		return iterate(self.left, self.right, self.reset, self.cycle, self.symbols)


Text.DEFAULT_COLOR = (255, 255, 255)
Text.DEFAULT_SIZE = 15
tl = Timeline()
nb_symbols = 4
nb_states = 4
nb_cells = 24
cells = []
readers = []
writers = []
Y = 10
W = 3


w  = W
ox = 10
oy = Y
master = Shape(0, oy, w, w, (255, 0, 0), z=-2)
cursor = Shape(ox, oy, w, w, (255, 0, 0), z=-2)
halt   = Shape(0, oy, w, w, (255, 0, 255), z=-3)
read_enable = Shape(0, oy, w, w, (255, 0, 0), z=2*nb_symbols+1)
left_enable = Shape(0, oy, w, w, (0, 255, 0), z=2*nb_symbols+2)
tl.add(Disappear(master), on=master)
tl.add(Disappear(read_enable), on=read_enable)
tl.add(Disappear(left_enable), on=left_enable)
tl.add(Appear(read_enable), on=master)
tl.add(Appear(left_enable), on=master)
tl.add(Appear(halt), on=halt)


for i in reversed(range(nb_symbols)):
	s = Shape(0, oy, w, w, (255, 255, 0), z=2*nb_symbols+5+i)
	readers.append(s)
	for reader in readers:
		tl.add(Disappear(reader), on=s)
	tl.add(Appear(reader), on=read_enable)

for i in range(nb_symbols-1):
	s = Shape(0, oy, w, w, (0, 255, 0), z=i*2)
	tl.add(Appear(s), on=master)
	tl.add(Disappear(s), on=s)
	writers.append(s)

x = 50
y = Document.HEIGHT/Document.SCALE-w
for i in range(nb_cells):
	dx = ox+i*(w+1)
	dy = w
	cell = Cell()
	cell.reset = Shape(dx, oy, w, w, (255, 0, 255, 1), z=-1)
	cell.cycle = Shape(dx, oy, w, w, (0, 255, 255), text=nb_symbols-1, z=2*nb_symbols)
	r1 = Shape(dx, oy+w, w, w)
	r2 = Shape(x+w+1+dx, y+dy, w, w, text="⯈")
	l1 = Shape(dx, oy+w, w, w)
	l2 = Shape(x+dx, y+dy, w, w, text="⯇")
	cell.right = Group(r1, r2, z=2*nb_symbols+3)
	cell.left  = Group(l1, l2, z=2*nb_symbols+4)

	for j in range(nb_symbols-1):
		color = (0, (j+1)*255/nb_symbols, (j+1)*255/nb_symbols)
		s = Shape(dx, oy, w, w, color, text=j, z=j*2+1)
		tl.add(Disappear(s), on=s)
		tl.add(Place(s), on=writers[j])
		tl.add(Disappear(readers[j+1]), on=s)
		cell.symbols.append(s)
	cosmetic = Shape(dx, oy, w, w, (0, 255, 255), text=nb_symbols-1, z=2*nb_symbols+1)

	for s in cell.symbols:
		tl.add(Appear(s), on=cell.reset)
		tl.add(Appear(s), on=cell.cycle)
	dx = cell.get_x()
	for s in cell.elements():
		tl.add(Place(s), on=cell.right)
		tl.add(Place(s), on=cell.left)

	tl.add(Appear(cell.reset), on=master)
	tl.add(Appear(cell.right), on=cell.reset)
	tl.add(Appear(cell.left), on=cell.reset)
	tl.add(Appear(master), on=cell.right)
	tl.add(Appear(master), on=cell.left)
	tl.add(Disappear(cell.reset), on=cell.reset)
	tl.add(Disappear(cell.right), on=left_enable)
	tl.add(Place(cursor, (((i+1)%nb_cells)*(w+1), 0)), on=cell.right)
	tl.add(Place(cursor, (((i-1)%nb_cells)*(w+1), 0)), on=cell.left)

	cells.append(cell)

for i, cell in enumerate(cells):
	right = cells[(i+1)%nb_cells]
	left  = cells[i-1]

	tl.add(Disappear(right.reset), on=cell.right)
	tl.add(Disappear(left.reset), on=cell.left)

	dx = right.get_x()
	for s in right.elements():
		tl.add(Place(s, (0, Y), relative=False), on=cell.right)
	dx = left.get_x()
	for s in left.elements():
		tl.add(Place(s, (0, Y), relative=False), on=cell.left)

first = cells[0]
dx = first.get_x()
tl.add(Disappear(first.reset))
for s in first.elements():
	tl.add(Place(s, (0, Y), relative=False))


w  = 4
ox = Document.WIDTH/Document.SCALE-w
oy = 1
symbol_setters = []
state_setters = []

for i in range(nb_symbols):
	s = Shape(ox, oy+i*(w+1), w, w, text=Text(i, centerX=False, left=0.5))
	symbol_setters.append(s)
for i in range(nb_symbols):
	s = symbol_setters[i]
	if i != 0:
		tl.add(Place(s, (w/2, 0)))
	tl.add(Place(s), on=s)
	for j in range(nb_symbols):
		other = symbol_setters[j]
		if i!=j:
			tl.add(Place(other, (w/2, 0)), on=s)
	for j, writer in enumerate(writers):
		if j >= i:
			tl.add(Place(writer), on=s)
		else:
			tl.add(Place(writer, relative=False), on=s)

for i in range(nb_states):
	s = Shape(ox, oy+(nb_symbols+i+0.5)*(w+1), w, w, text=Text(chr(ord("A")+i), centerX=False, left=0.5))
	state_setters.append(s)
for i, s in enumerate(state_setters):
	if i != 0:
		tl.add(Place(s, (w/2, 0)))
	tl.add(Place(s), on=s)
	for j, other in enumerate(state_setters):
		if i != j:
			tl.add(Place(other, (w/2, 0)), on=s)

right = Shape(ox, oy+(nb_symbols+nb_states+2)*(w+1), w, w, text=Text("⯈", centerX=False, left=0.5))
left  = Shape(ox, oy+(nb_symbols+nb_states+1)*(w+1), w, w, text=Text("⯇", centerX=False, left=0.5))
tl.add(Place(left_enable), on=left)
tl.add(Place(left_enable, relative=False), on=right)

tl.add(Place(right, (w/2, 0)))
tl.add(Place(right), on=right)
tl.add(Place(left, (w/2, 0)), on=right)
tl.add(Place(left), on=left)
tl.add(Place(right, (w/2, 0)), on=left)

stop  = Shape(ox, oy+(nb_symbols+nb_states+3)*(w+1), w, w, (255, 0, 0), text=Text("■", centerX=False, left=0.5))
tl.add(Place(stop, (w/2, 0)))
tl.add(Place(stop), on=stop)
tl.add(Place(halt), on=stop)
tl.add(Place(stop, (w/2, 0), click=True), on=stop)
tl.add(Place(halt, relative=False), on=stop)


w  = W
ox = 10+w
oy = 40
dx = -ox
dy = Y-oy
Shape(ox-w, oy-w, (nb_states+2)*(w+1)-3, (nb_symbols+2)*(w+1)-3, (255, 0, 255), z=3*nb_symbols+7)
transitions = [[None]*nb_symbols for _ in range(nb_states)]
for i in range(nb_states):
	for j in range(nb_symbols):
		color = (0, (j+1)*255/nb_symbols, (j+1)*255/nb_symbols)
		text = chr(ord("A")+i)+str(j)
		t0 = Shape(ox+(w+1)*i, oy+(w+1)*j, w, w, color, text=text)
		t1 = Shape(ox-dx+(w+1)*i*2, oy-dy+(w+1)*j*2, w, w, color, text=text)
		transitions[i][j] = Group(t0, t1, z=3*nb_symbols+6)
for i in range(nb_states):
	for j in range(nb_symbols):
		s = transitions[i][j]
		tl.add(FadeOut(s, repeat=0.5), on=s)
		tl.add(Appear(s), on=readers[j])
		tl.add(Disappear(s), on=master)
		tl.add(Appear(master), on=s)
		for k, setter in enumerate(state_setters):
			if k == i:
				tl.add(Place(s, (dx-i*(w+1), dy-j*(w+1))), on=setter)
				if i == 0:
					tl.add(Place(s, (dx-i*(w+1), dy-j*(w+1))))
			else:
				tl.add(Place(s), on=setter)
		for obj in iterate(symbol_setters, state_setters, left, right, stop):
			tl.add(SlideOut(obj, Animation.RIGHT, repeat=0.001), on=s)
		for obj in iterate(writers, left_enable, halt, *transitions):
			tl.add(SlideOut(obj, Animation.LEFT, repeat=0.001), on=s)


tl.add(Place(master, relative=False))
tl.add(Place(halt, relative=False))
tl.add(Disappear(halt))
tl.add(Disappear(left_enable))
for writer in writers:
	tl.add(Disappear(writer))

tl.add(Disappear(master, click=True))
tl.add(Place(master))
tl.add(Appear(halt))
tl.add(Place(halt, relative=False))
for reader in readers:
	tl.add(Appear(reader))
for transition in iterate(*transitions):
	tl.add(Disappear(transition))
for cell in cells:
	tl.add(Disappear(cell.right))
	tl.add(Disappear(cell.left))
	tl.add(Disappear(cell.cycle))

tl.add(Disappear(master, click=True), on=master)
for cell in cells:
	tl.add(Disappear(cell.right), on=master)
	tl.add(Disappear(cell.left), on=master)


shapes = Shape.dump()
slide = Slide("turing_machine", shapes, tl)
doc = Document("main", [slide])
doc.save()
