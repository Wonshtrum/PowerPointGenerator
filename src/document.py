from timeline import Timeline


class Document:
	# 1cm = 360 000
	HEIGHT = 6858000
	WIDTH = 12192000
	SCALE = 100000

	def relative_pos(x, y):
		return x/Document.WIDTH, y/Document.HEIGHT

	def __init__(self, path, slides=None):
		self.path = path
		self.slides = slides or []

	def save(self):
		n = len(self.slides)
		for slide in self.slides:
			slide.save(self.path)

		with open(f"{self.path}/ppt/_rels/presentation.xml.rels", "w") as fin:
			fin.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
	<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
	"""+"\n\t".join(
	f'<Relationship Id="rId{2+i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/{slide.name}.xml"/>'
	for i, slide in enumerate(self.slides))+f"""
	<Relationship Id="rId{n+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>
	<Relationship Id="rId{n+3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>
	<Relationship Id="rId{n+4}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
	<Relationship Id="rId{n+5}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>
</Relationships>""")

		with open(f"{self.path}/ppt/presentation.xml", "w") as fin:
			fin.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1">
	<p:sldMasterIdLst>
		<p:sldMasterId id="2147483648" r:id="rId1"/>
	</p:sldMasterIdLst>
	<p:sldIdLst>"""+"\n\t\t".join(
		f'<p:sldId id="{i+256}" r:id="rId{i+2}"/>'
		for i in range(n))+f"""
	</p:sldIdLst>
	<p:sldSz cx="{Document.WIDTH}" cy="{Document.HEIGHT}"/>
	<p:notesSz cx="6858000" cy="9144000"/>
	<p:defaultTextStyle>
		<a:defPPr>
			<a:defRPr lang="fr-FR"/>
		</a:defPPr>
	</p:defaultTextStyle>
</p:presentation>""")


class Slide:
	def __init__(self, name, shapes=None, timeline=None):
		self.name = name
		self.shapes = shapes or []
		self.timeline = timeline or Timeline()

	def save(self, path):
		with open(f"{path}/ppt/slides/_rels/{self.name}.xml.rels", "w") as fin:
			fin.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>""")

		with open(f"{path}/ppt/slides/{self.name}.xml", "w") as fin:
			fin.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
	<p:cSld>
		<p:spTree>
			<p:nvGrpSpPr>
				<p:cNvPr name="" id="1"/>
				<p:cNvGrpSpPr/>
				<p:nvPr/>
			</p:nvGrpSpPr>
			<p:grpSpPr>
				<a:xfrm>
					<a:off y="0" x="0"/>
					<a:ext cy="0" cx="0"/>
					<a:chOff y="0" x="0"/>
					<a:chExt cy="0" cx="0"/>
				</a:xfrm>
			</p:grpSpPr>"""+"".join(shape.save() for shape in self.shapes)+f"""
		</p:spTree>
	</p:cSld>
	<p:clrMapOvr>
		<a:masterClrMapping/>
	</p:clrMapOvr>
	{self.timeline.save()}
</p:sld>""")


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

	def __init__(self, x, y, cx, cy, color="000000", name="shape", ignore=False):
		self.name = name
		self.color = color
		self.x = int(x*Document.SCALE)
		self.y = int(y*Document.SCALE)
		self.cx = int(cx*Document.SCALE)
		self.cy = int(cy*Document.SCALE)
		self.id = Shape.get_id()
		if not ignore:
			Shape.cache.append(self)

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

	def save(self):
		return f"""
			<p:sp>
				<p:nvSpPr>
					<p:cNvPr name="{self.name}" id="{self.id}"/>
					<p:cNvSpPr/>
					<p:nvPr/>
				</p:nvSpPr>
				<p:spPr>
					<a:xfrm>
						<a:off x="{self.x}" y="{self.y}"/>
						<a:ext cx="{self.cx}" cy="{self.cy}"/>
					</a:xfrm>
					<a:prstGeom prst="rect">
						<a:avLst/>
					</a:prstGeom>
					<a:solidFill>
						<a:srgbClr val="{self.color}"/>
					</a:solidFill>
				</p:spPr>
			</p:sp>"""


class Group:
	def __init__(self, *shapes, name="group"):
		self.name = name
		self.shapes = shapes
		self.id = Shape.get_id()

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

	def save(self):
		x = self.get_x()
		y = self.get_y()
		cx = self.get_cx()
		cy = self.get_cy()
		return f"""
			<p:grpSp>
				<p:nvGrpSpPr>
					<p:cNvPr name="{self.name}" id="{self.id}"/>
					<p:cNvGrpSpPr/>
					<p:nvPr/>
				</p:nvGrpSpPr>
				<p:grpSpPr>
					<a:xfrm>
						<a:off x="{x}" y="{y}"/>
						<a:ext cx="{cx}" cy="{cy}"/>
						<a:chOff x="{x}" y="{y}"/>
						<a:chExt cx="{cx}" cy="{cy}"/>
					</a:xfrm>
				</p:grpSpPr>"""+"\n".join(shape.save() for shape in self.shapes)+"""
			</p:grpSp>"""