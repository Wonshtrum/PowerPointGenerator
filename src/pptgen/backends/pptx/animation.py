from pptgen.document import Document
from pptgen.timeline import Timeline
from pptgen.animation import *


def animation_to_pptx(obj):
	return f"""
							<p:par>
								<p:cTn id="{Timeline.get_id()}" nodeType="{Animation.CLICK_EFFECT if obj.click else Animation.WITH_EFFECT}" presetClass="{obj.preset}" presetID="{obj.preset_id}" presetSubtype="{obj.preset_subtype}" {f'repeatCount="{obj.repeat}" ' if obj.repeat!=1000 else ""}fill="hold">
									<p:stCondLst>
										<p:cond delay="{obj.delay}"/>
									</p:stCondLst>
									<p:childTnLst>
										{spec(obj)}
									</p:childTnLst>
								</p:cTn>
							</p:par>"""


def sub_spec_anim(obj, dur=None, *attributes):
	result = ""
	if dur is not None:
		result += f"""
											<p:cTn id="{Timeline.get_id()}" dur="{dur}" fill="hold"/>"""
	result += f"""
											<p:tgtEl>
												<p:spTgt spid="{obj.target}"/>
											</p:tgtEl>"""
	if attributes:
		result += f"""
											<p:attrNameLst>"""+"".join(f"""
												<p:attrName>{attribute}</p:attrName>""" for attribute in attributes)+"""
											</p:attrNameLst>"""
	return result

def spec_set(obj, attribute, value, on_sart=True):
	return f"""
									<p:set>
										<p:cBhvr>
											<p:cTn id="{Timeline.get_id()}" dur="1" fill="hold">
												<p:stCondLst>
													<p:cond delay="{0 if on_sart else obj.dur-1}"/>
												</p:stCondLst>
											</p:cTn>
											{sub_spec_anim(obj, None, attribute)}
										</p:cBhvr>
										<p:to>
											<p:strVal val="{value}"/>
										</p:to>
									</p:set>"""

def spec_anim_lerp(obj, attribute, value1, value2):
	return f"""
									<p:anim valueType="num" calcmode="lin">
										<p:cBhvr additive="base">
											{sub_spec_anim(obj, obj.dur, attribute)}
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

def spec_anim_effect(obj, filter, transition):
	return f"""
									<p:animEffect filter="{filter}" transition="{transition}">
										<p:cBhvr>
											{sub_spec_anim(obj, obj.dur)}
										</p:cBhvr>
									</p:animEffect>"""


def svg_path(obj):
	if obj.relative:
		ox = 0
		oy = 0
	else:
		ox = -obj.shape.get_x()
		oy = -obj.shape.get_y()
	if obj.centered:
		ox -= obj.shape.get_cx()/2
		oy -= obj.shape.get_cy()/2
	path = [Document.relative_pos(x*Document.SCALE+ox, y*Document.SCALE+oy) for x, y in obj.path]
	return f"M {path[0][0]} {path[0][1]} "+" ".join(f"L {pos[0]} {pos[1]}" for i,pos in enumerate(path[1:]))


def spec(obj):
	if isinstance(obj, Appear):
		return spec_set(obj, "style.visibility", "visible")

	elif isinstance(obj, Disappear):
		return spec_set(obj, "style.visibility", "hidden")


	elif isinstance(obj, FadeIn):
		return (spec_set(obj, "style.visibility", "visible")+
			spec_anim_effect(obj, "fade", "in"))

	elif isinstance(obj, FadeOut):
		return (spec_set(obj, "style.visibility", "hidden", False)+
			spec_anim_effect(obj, "fade", "out"))


	elif isinstance(obj, SlideIn):
		_, x, y = SlideIn.DIRECTIONS[obj.dir]
		return (spec_set(obj, "style.visibility", "visible")+
			spec_anim_lerp(obj, "ppt_x", x, "#ppt_x")+
			spec_anim_lerp(obj, "ppt_y", y, "#ppt_y"))

	elif isinstance(obj, SlideOut):
		_, x, y = SlideOut.DIRECTIONS[obj.dir]
		return (spec_set(obj, "style.visibility", "hidden", False)+
			spec_anim_lerp(obj, "ppt_x", "ppt_x", x)+
			spec_anim_lerp(obj, "ppt_y", "ppt_y", y))

	elif isinstance(obj, Path):
		return f"""
									<p:animMotion ptsTypes="{"A"*len(obj.path)}" rAng="0" pathEditMode="{"relative" if obj.relative else "fixed"}" path="{svg_path(obj)}" origin="layout">
										<p:cBhvr>
											{sub_spec_anim(obj, obj.dur, "ppt_x", "ppt_y")}
										</p:cBhvr>
									</p:animMotion>"""

	elif isinstance(obj, Rotation):
		return f"""
									<p:animRot by="{obj.angle}">
										<p:cBhvr>
											{sub_spec_anim(obj, obj.dur, "r")}
										</p:cBhvr>
									</p:animRot>"""


	elif isinstance(obj, Scale):
		return f"""
									<p:animScale>
										<p:cBhvr>
											{sub_spec_anim(obj, obj.dur)}
										</p:cBhvr>
										<p:by x="{obj.scale_x}" y="{obj.scale_y}"/>
									</p:animScale>"""

	raise NotImplementedError