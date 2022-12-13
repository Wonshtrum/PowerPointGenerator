from .timeline import Timeline


class Document:
	# 1cm = 360 000
	HEIGHT = 6858000
	WIDTH  = 12192000
	SCALE  = 100000
	COMPRESS = True

	def relative_pos(x, y):
		return x/Document.WIDTH, y/Document.HEIGHT

	def __init__(self, path, slides=None):
		self.path = path
		self.slides = slides or []


class Slide:
	def __init__(self, name, shapes=None, timeline=None):
		self.name = name
		self.shapes = shapes or []
		self.timeline = timeline or Timeline()


def wrap(obj, cls, default=None):
	if obj is None:
		if default is None:
			return cls()
		return cls(default)
	if isinstance(obj, cls):
		return obj
	return cls(obj)


class Color:
	def __init__(self, color=(0,0,0), alpha=0):
		self.color = f"{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}"
		if len(color) == 4:
			alpha = color[3]
		self.alpha = int(1000*alpha)


class Style:
	DEFAULT_FILL = (0, 0, 0)
	DEFAULT_OUTLINE = (0, 0, 0)

	def __init__(self, fill=None, outline=None, width=0):
		self.fill = wrap(fill, Color, Style.DEFAULT_FILL)
		self.outline = wrap(outline, Color, Style.DEFAULT_OUTLINE)
		self.width = width*Document.SCALE


class Text:
	DEFAULT_COLOR = (0, 0, 0)
	DEFAULT_SIZE = 18

	def __init__(self, content=None, color=None, size=None, centerX=True, centerY=True, top=0, bottom=0, right=0, left=0):
		self.content = content
		self.color = wrap(color, Color, Text.DEFAULT_COLOR)
		self.size = int((size or Text.DEFAULT_SIZE)*100)
		self.centerX = centerX
		self.centerY = centerY
		self.mt = int(top*Document.SCALE)
		self.mb = int(bottom*Document.SCALE)
		self.mr = int(right*Document.SCALE)
		self.ml = int(left*Document.SCALE)


def scale_on_demand(f):
	def wrapper(self, scale=False):
		if scale:
			return f(self)/Document.SCALE
		return f(self)
	return wrapper


class Shape:
	id = 10
	def get_id():
		Shape.id += 1
		return Shape.id

	cache = []
	def dump():
		cache = Shape.cache
		Shape.cache = []
		return cache

	def __init__(self, x, y, cx, cy, style=None, text=None, name="shape", ignore=False, z=0):
		self.name = name
		self.z = z
		self.x = int(x*Document.SCALE)
		self.y = int(y*Document.SCALE)
		self.cx = int(cx*Document.SCALE)
		self.cy = int(cy*Document.SCALE)
		self.id = Shape.get_id()
		if not ignore:
			Shape.cache.append(self)
		self.style = wrap(style, Style)
		self.text = wrap(text, Text)

	def contains(self, tx, ty):
		x, y, cx, cy = self.x, self.y, self.cx, self.cy
		return tx >= x and tx <= x+cx and ty >= y and ty <= y+cy

	@scale_on_demand
	def get_x(self):
		return self.x
	@scale_on_demand
	def get_y(self):
		return self.y
	@scale_on_demand
	def get_cx(self):
		return self.cx
	@scale_on_demand
	def get_cy(self):
		return self.cy


class Group:
	def __init__(self, *shapes, name="group", ignore=False, z=0):
		self.name = name
		self.z = z
		self.shapes = shapes
		self.id = Shape.get_id()
		if not ignore:
			for shape in shapes:
				if shape in Shape.cache:
					Shape.cache.remove(shape)
			Shape.cache.append(self)

	def contains(self, tx, ty):
		return any(shape.contains(tx, ty) for shape in self.shapes)

	@scale_on_demand
	def get_x(self):
		return min(shape.get_x() for shape in self.shapes)
	@scale_on_demand
	def get_y(self):
		return min(shape.get_y() for shape in self.shapes)
	@scale_on_demand
	def get_cx(self):
		return max(shape.get_x()+shape.get_cx() for shape in self.shapes)-self.get_x()
	@scale_on_demand
	def get_cy(self):
		return max(shape.get_y()+shape.get_cy() for shape in self.shapes)-self.get_y()