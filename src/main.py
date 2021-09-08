from document import *
from animation import *


rect1 = Shape(10, 10, 10, 10, "FF0000")
rect2 = Shape(20, 20, 10, 10, "00FF00")
rect3 = Shape(30, 30, 10, 10, "0000FF")
rect4 = Shape(40, 40, 10, 10, "FFFF00")
grp1 = Group(rect1, rect2)
grp2 = Group(grp1, rect3)

tl1 = Timeline()
delay = 0
dur = 0.4
for dir in Animation.DIRECTIONS:
	tl1.add(SlideIn(rect1, dir, dur, delay, 0.5, False))
	delay += dur/2
	tl1.add(SlideOut(rect1, dir, dur, delay, 0.5, False))
	delay += dur/2

p = [(0,0), (20,0), (20,20), (0,20)]
tl2 = Timeline(SlideIn(rect4, Animation.UP, 1, 1, 0.5, False), SlideOut(rect4, Animation.LEFT, 0.5, 2, 0.5, False), Disappear(rect4), Appear(rect4, 0.5, False), Path(rect4, p, 0.2, 0, 0.5))
tl2.add(Appear(rect4, 0, False), Disappear(rect4, 1, False), Appear(rect4, 0.5), Path(rect4, p, 0.5, 0, 2.5, relative=True), on=grp2)
tl2.add(Appear(rect4, 0, True), Disappear(rect4, 1, False), Appear(rect4, 0.5), Path(rect4, p, 1, relative=True, centered=True), on=rect4)

slide1 = Slide("slide1", [rect1], tl1)
slide2 = Slide("slide2", [grp2, rect4], tl2)
doc = Document("out", [slide1, slide2])
doc.save()