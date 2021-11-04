from .document import Document
from .timeline import Timeline


class Animation:
	CLICK_EFFECT = "clickEffect"
	WITH_EFFECT  = "withEffect"
	AFTER_EFFECT = "afterEffect"

	ENTR = "entr"
	EMPH = "emph"
	PATH = "path"
	EXIT = "exit"

	MIN_TIME = 0.01

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

	def sub_spec_anim(self, dur=None, *attributes):
		result = ""
		if dur is not None:
			result += f"""
											<p:cTn id="{Timeline.get_id()}" dur="{dur}" fill="hold"/>"""
		result += f"""
											<p:tgtEl>
												<p:spTgt spid="{self.target}"/>
											</p:tgtEl>"""
		if attributes:
			result += f"""
											<p:attrNameLst>"""+"".join(f"""
												<p:attrName>{attribute}</p:attrName>""" for attribute in attributes)+"""
											</p:attrNameLst>"""
		return result

	def spec_set(self, attribute, value, on_sart=True):
		return f"""
									<p:set>
										<p:cBhvr>
											<p:cTn id="{Timeline.get_id()}" dur="1" fill="hold">
												<p:stCondLst>
													<p:cond delay="{0 if on_sart else self.dur-1}"/>
												</p:stCondLst>
											</p:cTn>
											{self.sub_spec_anim(None, attribute)}
										</p:cBhvr>
										<p:to>
											<p:strVal val="{value}"/>
										</p:to>
									</p:set>"""

	def spec_anim_lerp(self, attribute, value1, value2):
		return f"""
									<p:anim valueType="num" calcmode="lin">
										<p:cBhvr additive="base">
											{self.sub_spec_anim(self.dur, attribute)}
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

	def spec_anim_effect(self, filter, transition):
		return f"""
									<p:animEffect filter="{filter}" transition="{transition}">
										<p:cBhvr>
											{self.sub_spec_anim()}
										</p:cBhvr>
									</p:animEffect>"""


class Appear(Animation):
	def __init__(self, shape, delay=0, click=False):
		super().__init__(shape, Animation.ENTR, 1, 0, 0, delay, 1, click)

	def spec(self):
		return self.spec_set("style.visibility", "visible")


class Disappear(Animation):
	def __init__(self, shape, delay=0, click=False):
		super().__init__(shape, Animation.EXIT, 1, 0, 0, delay, 1, click)

	def spec(self):
		return self.spec_set("style.visibility", "hidden")


class FadeIn(Animation):
	def __init__(self, shape, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		super().__init__(shape, Animation.ENTR, 10, 0, dur, delay, repeat, click)

	def spec(self):
		return (self.spec_set("style.visibility", "visible")+
			self.spec_anim_effect("fade", "in"))


class FadeOut(Animation):
	def __init__(self, shape, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		super().__init__(shape, Animation.EXIT, 10, 0, dur, delay, repeat, click)

	def spec(self):
		return (self.spec_set("style.visibility", "hidden", False)+
			self.spec_anim_effect("fade", "out"))


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

	def __init__(self, shape, dir, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		preset_subtype, _, _ = SlideIn.DIRECTIONS[dir]
		super().__init__(shape, Animation.ENTR, 2, preset_subtype, dur, delay, repeat, click)
		self.dir = dir

	def spec(self):
		_, x, y = SlideIn.DIRECTIONS[self.dir]
		return (self.spec_set("style.visibility", "visible")+
			self.spec_anim_lerp("ppt_x", x, "#ppt_x")+
			self.spec_anim_lerp("ppt_y", y, "#ppt_y"))


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

	def __init__(self, shape, dir, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		preset_subtype, _, _ = SlideOut.DIRECTIONS[dir]
		super().__init__(shape, Animation.EXIT, 2, preset_subtype, dur, delay, repeat, click)
		self.dir = dir

	def spec(self):
		_, x, y = SlideOut.DIRECTIONS[self.dir]
		return (self.spec_set("style.visibility", "hidden", False)+
			self.spec_anim_lerp("ppt_x", "ppt_x", x)+
			self.spec_anim_lerp("ppt_y", "ppt_y", y))


class Path(Animation):
	def __init__(self, shape, path, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False, relative=True, centered=False):
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
											{self.sub_spec_anim(self.dur, "ppt_x", "ppt_y")}
										</p:cBhvr>
									</p:animMotion>"""


class Place(Path):
	def __init__(self, shape, position=(0, 0), dur=Animation.MIN_TIME, delay=0, click=False, relative=True, centered=False):
		super().__init__(shape, [position, position], dur, delay, 1, click, relative, centered)


class Rotation(Animation):
	def __init__(self, shape, angle=180, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		super().__init__(shape, Animation.EMPH, 8, 0, dur, delay, repeat, click)
		self.angle = int(angle*60000)

	def spec(self):
		return f"""
									<p:animRot by="{self.angle}">
										<p:cBhvr>
											{self.sub_spec_anim(self.dur, "r")}
										</p:cBhvr>
									</p:animRot>"""


class Scale(Animation):
	def __init__(self, shape, scale_x=100, scale_y=100, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		super().__init__(shape, Animation.EMPH, 6, 0, dur, delay, repeat, click)
		self.scale_x = int(scale_x*1000)
		self.scale_y = int(scale_y*1000)

	def spec(self):
		return f"""
									<p:animScale>
										<p:cBhvr>
											{self.sub_spec_anim(self.dur)}
										</p:cBhvr>
										<p:by x="{self.scale_x}" y="{self.scale_y}"/>
									</p:animScale>"""