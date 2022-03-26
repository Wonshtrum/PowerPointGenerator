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


class Appear(Animation):
	def __init__(self, shape, delay=0, click=False):
		super().__init__(shape, Animation.ENTR, 1, 0, 0, delay, 1, click)


class Disappear(Animation):
	def __init__(self, shape, delay=0, click=False):
		super().__init__(shape, Animation.EXIT, 1, 0, 0, delay, 1, click)


class FadeIn(Animation):
	def __init__(self, shape, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		super().__init__(shape, Animation.ENTR, 10, 0, dur, delay, repeat, click)


class FadeOut(Animation):
	def __init__(self, shape, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		super().__init__(shape, Animation.EXIT, 10, 0, dur, delay, repeat, click)


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


class Path(Animation):
	def __init__(self, shape, path, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False, relative=True, centered=False):
		super().__init__(shape, Animation.PATH, 0, 1, dur, delay, repeat, click)
		self.shape = shape
		self.path = path
		self.centered = centered
		self.relative = relative


class Place(Path):
	def __init__(self, shape, position=(0, 0), dur=Animation.MIN_TIME, delay=0, click=False, relative=True, centered=False):
		super().__init__(shape, [position, position], dur, delay, 1, click, relative, centered)


class Rotation(Animation):
	def __init__(self, shape, angle=180, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		super().__init__(shape, Animation.EMPH, 8, 0, dur, delay, repeat, click)
		self.angle = int(angle*60000)


class Scale(Animation):
	def __init__(self, shape, scale_x=100, scale_y=100, dur=Animation.MIN_TIME, delay=0, repeat=1, click=False):
		super().__init__(shape, Animation.EMPH, 6, 0, dur, delay, repeat, click)
		self.scale_x = int(scale_x*1000)
		self.scale_y = int(scale_y*1000)