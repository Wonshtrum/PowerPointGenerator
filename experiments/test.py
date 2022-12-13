from pptgen import *
from pptgen.serializer import save_to_pptx
from pptgen.runner import tk_run

tl = Timeline()

target = Shape(0, 0, 1, 1)
button = Shape(2, 0, 1, 1)

tl.add(Disappear(target))
tl.add(Disappear(button))
tl.add(Appear(target))
tl.add(Appear(button, click=True))
tl.add(Appear(button, click=True))
tl.add(Appear(target), on=button)
tl.add(Disappear(target, click=True), on=button)

shapes = Shape.dump()
slide = Slide("test", shapes, tl)
tk_run(slide, 800, 400, 40/Document.SCALE)