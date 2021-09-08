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

	UP         = 0
	UP_RIGHT   = 1
	RIGHT      = 2
	DOWN_RIGHT = 3
	DOWN       = 4
	DOWN_LEFT  = 5
	LEFT       = 6
	UP_LEFT    = 7
	DIRECTIONS = list(range(8))

	def __init__(self, shape, preset, preset_id, preset_subtype, dur, delay, repeat, click):
		self.target = shape.id
		self.preset = preset
		self.preset_id = preset_id
		self.preset_subtype = preset_subtype
		self.dur = max(1, int(dur*1000))
		self.delay = int(delay*1000)
		self.repeat = int(repeat*1000)
		self.click = click

	def save(self):
		return f"""
						<p:par>
							<p:cTn id="{Timeline.get_id()}" nodeType="{Animation.CLICK_EFFECT if self.click else Animation.WITH_EFFECT}" presetClass="{self.preset}" presetID="{self.preset_id}" presetSubtype="{self.preset_subtype}" {f'repeatCount="{self.repeat}" ' if self.repeat!=1000 else ""}fill="hold">
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

	def spec_anim(self, attribute, value1, value2):
		return f"""
									<p:anim valueType="num" calcmode="lin">
										<p:cBhvr additive="base">
											<p:cTn id="{Timeline.get_id()}" dur="{self.dur}" fill="hold"/>
											<p:tgtEl>
												<p:spTgt spid="{self.target}"/>
											</p:tgtEl>
											<p:attrNameLst>
												<p:attrName>{attribute}</p:attrName>
											</p:attrNameLst>
										</p:cBhvr>
										<p:tavLst>
											<p:tav tm="0">
												<p:val>
													<p:strVal val="{value1}"/>
												</p:val>
											</p:tav>
											<p:tav tm="100000">
												<p:val>
													<p:strVal val="{value2}"/>
												</p:val>
											</p:tav>
										</p:tavLst>
									</p:anim>"""


class Appear(Animation):
	def __init__(self, shape, delay=0, click=True):
		super().__init__(shape, Animation.ENTR, 1, 0, 0, delay, 1, click)

	def spec(self):
		return self.spec_set("style.visibility", "visible")


class Disappear(Animation):
	def __init__(self, shape, delay=0, click=True):
		super().__init__(shape, Animation.EXIT, 1, 0, 0, delay, 1, click)

	def spec(self):
		return self.spec_set("style.visibility", "hidden")


class SlideIn(Animation):
	DIRECTIONS = {
		Animation.UP         : ( 4, "#ppt_x",     "1+#ppt_h/2"),
		Animation.UP_RIGHT   : (12, "0-#ppt_w/2", "1+#ppt_h/2"),
		Animation.RIGHT      : ( 8, "0-#ppt_w/2", "#ppt_y"),
		Animation.DOWN_RIGHT : ( 9, "0-#ppt_w/2", "0-#ppt_h/2"),
		Animation.DOWN       : ( 1, "#ppt_x",     "0-#ppt_h/2"),
		Animation.DOWN_LEFT  : ( 3, "1+#ppt_w/2", "0-#ppt_h/2"),
		Animation.LEFT       : ( 2, "1+#ppt_w/2", "#ppt_y"),
		Animation.UP_LEFT    : ( 6, "1+#ppt_w/2", "1+#ppt_h/2")
	}

	def __init__(self, shape, dir, dur=0, delay=0, repeat=1, click=True):
		preset_subtype, _, _ = SlideIn.DIRECTIONS[dir]
		super().__init__(shape, Animation.ENTR, 2, preset_subtype, dur, delay, repeat, click)
		self.dir = dir

	def spec(self):
		_, x, y = SlideIn.DIRECTIONS[self.dir]
		return (self.spec_set("style.visibility", "visible")+
			self.spec_anim("ppt_x", x, "#ppt_x")+
			self.spec_anim("ppt_y", y, "#ppt_y"))

class SlideOut(Animation):
	DIRECTIONS = {
		Animation.DOWN       : ( 4, "ppt_x",     "1+ppt_h/2"),
		Animation.DOWN_LEFT  : (12, "0-ppt_w/2", "1+ppt_h/2"),
		Animation.LEFT       : ( 8, "0-ppt_w/2", "ppt_y"),
		Animation.UP_LEFT    : ( 9, "0-ppt_w/2", "0-ppt_h/2"),
		Animation.UP         : ( 1, "ppt_x",     "0-ppt_h/2"),
		Animation.UP_RIGHT   : ( 3, "1+ppt_w/2", "0-ppt_h/2"),
		Animation.RIGHT      : ( 2, "1+ppt_w/2", "ppt_y"),
		Animation.DOWN_RIGHT : ( 6, "1+ppt_w/2", "1+ppt_h/2")
	}

	def __init__(self, shape, dir, dur=0, delay=0, repeat=1, click=True):
		preset_subtype, _, _ = SlideOut.DIRECTIONS[dir]
		super().__init__(shape, Animation.EXIT, 2, preset_subtype, dur, delay, repeat, click)
		self.dir = dir

	def spec(self):
		_, x, y = SlideOut.DIRECTIONS[self.dir]
		return (self.spec_set("style.visibility", "hidden", False)+
			self.spec_anim("ppt_x", "ppt_x", x)+
			self.spec_anim("ppt_y", "ppt_y", y))

class Path(Animation):
	def __init__(self, shape, path, dur=0, delay=0, repeat=1, click=True, relative=False, centered=False):
		super().__init__(shape, Animation.PATH, 0, 1, dur, delay, repeat, click)
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
									</p:animMotion>"""