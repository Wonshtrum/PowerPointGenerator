from document import Document
from timeline import Timeline


class Animation:
	CLICK_EFFECT = "clickEffect"
	WITH_EFFECT  = "withEffect"
	AFTER_EFFECT = "afterEffect"

	ENTR = "entr"
	EMPH = "emph"
	PATH = "path"
	EXIT = "exit"

	def __init__(self, shape, preset, id, delay, dur, repeat, click):
		self.target = shape.id
		self.preset = preset
		self.id = id
		self.delay = int(delay*1000)
		self.dur = max(1, int(dur*1000))
		self.repeat = int(repeat*1000)
		self.click = click

	def save(self):
		return f"""
						<p:par>
							<p:cTn id="{Timeline.get_id()}" nodeType="{Animation.CLICK_EFFECT if self.click else Animation.WITH_EFFECT}" presetClass="{self.preset}" presetID="{self.id}" repeatCount="{self.repeat}" fill="hold" presetSubtype="0">
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

	def spec_set(self, attribute, value, on_sart=True):
		return f"""
									<p:set>
										<p:cBhvr>
											<p:cTn id="{Timeline.get_id()}" dur="1" fill="hold">
												<p:stCondLst>
													<p:cond delay="{0 if on_sart else self.dur-1}"/>
												</p:stCondLst>
											</p:cTn>
											<p:tgtEl>
												<p:spTgt spid="{self.target}"/>
											</p:tgtEl>
											<p:attrNameLst>
												<p:attrName>{attribute}</p:attrName>
											</p:attrNameLst>
										</p:cBhvr>
										<p:to>
											<p:strVal val="{value}"/>
										</p:to>
									</p:set>"""


class Appear(Animation):
	def __init__(self, shape, delay=0, click=True):
		super().__init__(shape, Animation.ENTR, 1, delay, 0, 1, click)

	def spec(self):
		return self.spec_set("style.visibility", "visible")


class Disappear(Animation):
	def __init__(self, shape, delay=0, click=True):
		super().__init__(shape, Animation.EXIT, 1, delay, 0, 1, click)

	def spec(self):
		return self.spec_set("style.visibility", "hidden")


class Path(Animation):
	def __init__(self, shape, path, dur=0, delay=0, repeat=1, click=True, relative=False, centered=False):
		super().__init__(shape, Animation.PATH, 0, delay, dur, repeat, click)
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
		path = [Document.relative_pos(x*Document.SCALE+ox, y*Document.SCALE+oy) for x, y in self.path]
		return f"M {path[0][0]} {path[0][1]} "+" ".join(f"L {pos[0]} {pos[1]}" for i,pos in enumerate(path[1:]))

	def spec(self):
		return f"""
									<p:animMotion ptsTypes="{"A"*len(self.path)}" rAng="0" pathEditMode="{"relative" if self.relative else "fixed"}" path="{self.svg_path()}" origin="layout">
										<p:cBhvr>
											<p:cTn id="{Timeline.get_id()}" dur="{self.dur}" fill="hold"/>
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