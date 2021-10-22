from pptgen import *


def iterate(*elements):
	for element in elements:
		try:
			for sub_element in element:
				yield sub_element
		except TypeError:
			yield element


tl = Timeline()
n_columns = 10
n_rows = 10

w = 2
matrix = [[Shape(x*(w+1), y*(w+1), w, w) for x in range(3)] for y in range(3)]
start = Shape(20, 0, w, w, (255, 0, 0))

w = 3
ox = 10
oy = 10
last = start
for y in range(n_rows):
	for x in range(n_columns):
		s  = Shape(ox+x*(w+1), oy+y*(w+1), w, w, z=0)
		s2 = Shape(ox+x*(w+1), oy+y*(w+1)+0.5, w, w, (255, 0, 0), z=1)
		tl.add(Disappear(matrix[(x+0)%3][0]), on=s)
		tl.add(Disappear(matrix[(x+1)%3][1]), on=s)
		tl.add(Disappear(matrix[(x+2)%3][2]), on=s)
		tl.add(Disappear(s), on=s)
		tl.add(Disappear(s2), on=s2)
		for i in range(3):
			tl.add(Appear(matrix[x%3][i]), on=s2)
		if x == 0:
			for _ in iterate(*matrix):
				tl.add(Appear(_), on=last)
		tl.add(Place(s, (20, 3), relative=False), on=last)
		tl.add(Place(s2, (20, 3.5), relative=False), on=last)
		last = s2


shapes = Shape.dump()
slide = Slide("rule110", shapes, tl)
doc = Document("rule110", [slide])
doc.save()