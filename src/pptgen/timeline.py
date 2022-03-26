class Timeline:
	id = 0
	def reset_id():
		Timeline.id = 0
	def get_id():
		Timeline.id += 1
		return Timeline.id

	def __init__(self, *animations):
		self.contexts = {"main":list(animations)}

	def add(self, *animations, on=None):
		if on is None:
			self.contexts["main"].extend(animations)
		elif on.id in self.contexts:
			self.contexts[on.id].extend(animations)
		else:
			self.contexts[on.id] = list(animations)