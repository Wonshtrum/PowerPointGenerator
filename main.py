SCALE = 100000


class Document:
	# 1cm = 360 000
	HEIGHT = 6858000
	WIDTH = 12192000

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
</Relationships>
""")

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


class Shape:
	id = 10
	def get_id():
		Shape.id += 1
		return Shape.id

	def __init__(self, x, y, cx, cy, color="000000", name="shape"):
		self.name = name
		self.color = color
		self.x = x*SCALE
		self.y = y*SCALE
		self.cx = cx*SCALE
		self.cy = cy*SCALE
		self.id = Shape.get_id()

	def get_x(self):
		return self.x
	def get_y(self):
		return self.y
	def get_cx(self):
		return self.cx
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

	def get_x(self):
		return min(shape.get_x() for shape in self.shapes)
	def get_y(self):
		return min(shape.get_y() for shape in self.shapes)
	def get_cx(self):
		return max(shape.get_x()+shape.get_cx() for shape in self.shapes)-self.get_x()
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


class Animation:
	id = 0
	def reset_id():
		Animation.id = 0
	def get_id():
		Animation.id += 1
		return Animation.id

	CLICK_EFFECT = "clickEffect"
	WITH_EFFECT  = "withEffect"
	AFTER_EFFECT = "afterEffect"

	ENTR = "entr"
	EMPH = "emph"
	PATH = "path"
	EXIT = "exit"

	def __init__(self, shape, preset, id, delay, dur, click):
		self.target = shape.id
		self.preset = preset
		self.id = id
		self.delay = int(delay*1000)
		self.dur = max(1, int(dur*1000))
		self.click = click

	def save(self):
		return f"""
						<p:par>
							<p:cTn id="{Animation.get_id()}" nodeType="{Animation.CLICK_EFFECT if self.click else Animation.WITH_EFFECT}" fill="hold" presetSubtype="0" presetClass="{self.preset}" presetID="{self.id}">
								<p:stCondLst>
									<p:cond delay="{self.delay}"/>
								</p:stCondLst>
								<p:childTnLst>
									{self.spec()}
								</p:childTnLst>
							</p:cTn>
						</p:par>"""

	def spec(self):
		raise NotImplementedError


class Appear(Animation):
	def __init__(self, shape, delay=0, click=True):
		super().__init__(shape, Animation.ENTR, 1, delay, 0, click)

	def spec(self):
		return f"""
									<p:set>
										<p:cBhvr>
											<p:cTn id="{Animation.get_id()}" dur="1" fill="hold">
												<p:stCondLst>
													<p:cond delay="0"/>
												</p:stCondLst>
											</p:cTn>
											<p:tgtEl>
												<p:spTgt spid="{self.target}"/>
											</p:tgtEl>
											<p:attrNameLst>
												<p:attrName>style.visibility</p:attrName>
											</p:attrNameLst>
										</p:cBhvr>
										<p:to>
											<p:strVal val="visible"/>
										</p:to>
									</p:set>"""


class Disappear(Animation):
	def __init__(self, shape, delay=0, click=True):
		super().__init__(shape, Animation.EXIT, 1, delay, 0, click)

	def spec(self):
		return f"""
									<p:set>
										<p:cBhvr>
											<p:cTn id="{Animation.get_id()}" dur="1" fill="hold">
												<p:stCondLst>
													<p:cond delay="0"/>
												</p:stCondLst>
											</p:cTn>
											<p:tgtEl>
												<p:spTgt spid="{self.target}"/>
											</p:tgtEl>
											<p:attrNameLst>
												<p:attrName>style.visibility</p:attrName>
											</p:attrNameLst>
										</p:cBhvr>
										<p:to>
											<p:strVal val="hidden"/>
										</p:to>
									</p:set>"""


class Path(Animation):
	def __init__(self, shape, path, dur=0, delay=0, click=True, relative=False, centered=False):
		super().__init__(shape, Animation.PATH, 0, delay, dur, click)
		self.shape = shape
		self.path = path
		self.centered = centered
		self.relative = relative

	def svg_path(self):
		if self.relative:
			ox = 0
			oy = 0
		else:
			ox = -self.shape.get_x()
			oy = -self.shape.get_y()
		if self.centered:
			ox -= self.shape.get_cx()/2
			oy -= self.shape.get_cy()/2
		path = [Document.relative_pos(x*SCALE+ox, y*SCALE+oy) for x, y in self.path]
		return f"M {path[0][0]} {path[0][1]} "+" ".join(f"L {pos[0]} {pos[1]}" for i,pos in enumerate(path[1:]))

	def spec(self):
		return f"""
									<p:animMotion ptsTypes="{"A"*len(self.path)}" rAng="0" pathEditMode="fixed" path="{self.svg_path()}" origin="layout">
										<p:cBhvr>
											<p:cTn id="{Animation.get_id()}" dur="{self.dur}" fill="hold"/>
											<p:tgtEl>
												<p:spTgt spid="{self.target}"/>
											</p:tgtEl>
											<p:attrNameLst>
												<p:attrName>ppt_x</p:attrName>
												<p:attrName>ppt_y</p:attrName>
											</p:attrNameLst>
										</p:cBhvr>
										<p:rCtr y="21875" x="12292"/>
									</p:animMotion>"""

class Timeline:
	def __init__(self, *animations):
		self.contexts = {"main":animations}

	def add(self, *animations, on=None):
		if on is None:
			self.contexts["main"].extend(animations)
		elif on in self.contexts:
			self.contexts[on.id].extend(animations)
		else:
			self.contexts[on.id] = animations

	def save_context(self, context):
		seq_id = Animation.get_id()
		result = """
					<p:seq nextAc="seek" concurrent="1">"""
		if context == "main":
			result += f"""
						<p:cTn id="{seq_id}" nodeType="mainSeq" dur="indefinite">
							<p:childTnLst>"""
		else:
			result += f"""
						<p:cTn id="{seq_id}" nodeType="interactiveSeq" restart="whenNotActive" fill="hold" evtFilter="cancelBubble">
							<p:stCondLst>
								<p:cond delay="0" evt="onClick">
									<p:tgtEl>
										<p:spTgt spid="{context}"/>
									</p:tgtEl>
								</p:cond>
							</p:stCondLst>
							<p:endSync delay="0" evt="end">
								<p:rtn val="all"/>
							</p:endSync>
							<p:childTnLst>"""
		if not self.contexts[context]:
			result += f"""
								<p:par>
									<p:cTn id="{Animation.get_id()}"/>
								</p:par>"""
		else:
			def add_group(result, group):
				return result + f"""
								<p:par>
									<p:cTn id="{Animation.get_id()}" fill="hold">
										<p:stCondLst>
											<p:cond delay="indefinite"/>
											{"" if group[0].click else f'<p:cond delay="0" evt="onBegin"><p:tn val="{seq_id}"/></p:cond>'}
										</p:stCondLst>
										<p:childTnLst>

											<p:par>
												<p:cTn id="{Animation.get_id()}" fill="hold">
													<p:stCondLst>
														<p:cond delay="0"/>
													</p:stCondLst>
													<p:childTnLst>"""+"".join(animation.save() for animation in group)+"""
													</p:childTnLst>
												</p:cTn>
											</p:par>

										</p:childTnLst>
									</p:cTn>
								</p:par>"""
			group = [self.contexts[context][0]]
			for animation in self.contexts[context][1:]:
				if not animation.click:
					group.append(animation)
				else:
					result = add_group(result, group)
					group = [animation]
			result = add_group(result, group)
		if context == "main":
			result += """
							</p:childTnLst>
						</p:cTn>
						<p:prevCondLst>
							<p:cond delay="0" evt="onPrev">
								<p:tgtEl>
									<p:sldTgt/>
								</p:tgtEl>
							</p:cond>
						</p:prevCondLst>
						<p:nextCondLst>
							<p:cond delay="0" evt="onNext">
								<p:tgtEl>
									<p:sldTgt/>
								</p:tgtEl>
							</p:cond>
						</p:nextCondLst>
					</p:seq>"""
		else:
			result += f"""
							</p:childTnLst>
						</p:cTn>
						<p:nextCondLst>
							<p:cond delay="0" evt="onClick">
								<p:tgtEl>
									<p:spTgt spid="{context}"/>
								</p:tgtEl>
							</p:cond>
						</p:nextCondLst>
					</p:seq>"""
		return result

	def save(self):
		Animation.reset_id()
		return f"""
	<p:timing>
		<p:tnLst>
			<p:par>
				<p:cTn id="{Animation.get_id()}" nodeType="tmRoot" restart="never" dur="indefinite">
					<p:childTnLst>"""+"".join(self.save_context(context) for context in self.contexts)+"""
					</p:childTnLst>
				</p:cTn>
			</p:par>
		</p:tnLst>
	</p:timing>"""


rect1 = Shape(10, 10, 10, 10, "FF0000")
rect2 = Shape(20, 20, 10, 10, "00FF00")
rect3 = Shape(30, 30, 10, 10, "0000FF")
rect4 = Shape(40, 40, 10, 10, "FFFF00")
grp1 = Group(rect1, rect2)
grp2 = Group(grp1, rect3)
p = [(0,0), (20,0), (20,20), (0,20)]
tl = Timeline(Appear(rect4, 0, False), Disappear(rect4, 1, False), Appear(rect4, 0.5), Path(rect4, p, 0.2))
tl.add(Appear(rect4, 0, False), Disappear(rect4, 1, False), Appear(rect4, 0.5), Path(rect4, p, 0.5, relative=True), on=grp2)
tl.add(Appear(rect4, 0, True), Disappear(rect4, 1, False), Appear(rect4, 0.5), Path(rect4, p, 1, relative=True, centered=True), on=rect4)
slide1 = Slide("slide1")
slide2 = Slide("slide2", [grp2, rect4], tl)
doc = Document("src", [slide1, slide2])
doc.save()