from pptgen.document import Document, Group
from pptgen.zipper import create_base
from .timeline import timeline_to_pptx


def document_to_pptx(obj):
	output = create_base(f"{obj.path}.pptx")

	n = len(obj.slides)
	for slide in obj.slides:
		slide_to_pptx(slide, output)

	output.put_file("ppt/_rels/presentation.xml.rels",
"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
	<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
	"""+"\n\t".join(
	f'<Relationship Id="rId{2+i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/{slide.name}.xml"/>'
	for i, slide in enumerate(obj.slides))+f"""
	<Relationship Id="rId{n+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>
	<Relationship Id="rId{n+3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>
	<Relationship Id="rId{n+4}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
	<Relationship Id="rId{n+5}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>
</Relationships>""", compress=Document.COMPRESS)

	output.put_file("ppt/presentation.xml",
"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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
</p:presentation>""", compress=Document.COMPRESS)

	output.close()


def slide_to_pptx(obj, output):
	output.put_file(f"ppt/slides/_rels/{obj.name}.xml.rels",
"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>""", compress=Document.COMPRESS)

	output.put_file(f"ppt/slides/{obj.name}.xml",
"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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
			</p:grpSpPr>"""+"".join(shape_to_pptx(shape) for shape in reversed(sorted(obj.shapes, key=lambda shape:shape.z)))+f"""
		</p:spTree>
	</p:cSld>
	<p:clrMapOvr>
		<a:masterClrMapping/>
	</p:clrMapOvr>
	{timeline_to_pptx(obj.timeline)}
</p:sld>""", compress=Document.COMPRESS)


def color_to_pptx(obj):
	return f"""
					<a:solidFill>
						<a:srgbClr val="{obj.color}"{"/>" if obj.alpha==0 else f'><a:alpha val="{obj.alpha}"/></a:srgbClr>'}
					</a:solidFill>"""


def style_to_pptx(obj):
	result = color_to_pptx(obj.fill)
	if obj.width != 0:
		result += f"""
					<a:ln w="{obj.width}">{color_to_pptx(obj.outline)}
					</a:ln>"""
	return result


def text_to_pptx(obj):
	if obj.content is None:
		return ""
	return f"""
					<p:txBody>
						<a:bodyPr bIns="{obj.mb}" rIns="{obj.mr}" tIns="{obj.mt}" lIns="{obj.ml}"{' anchor="ctr"' if obj.centerY else ""}/>
						<a:lstStyle/>
						<a:p>{'<a:pPr algn="ctr"/>' if obj.centerX else ""}
							<a:r>
								<a:rPr sz="{obj.size}">{color_to_pptx(obj.color)}
								</a:rPr>
								<a:t>{obj.content}</a:t>
							</a:r>
						</a:p>
					</p:txBody>"""


def shape_to_pptx(obj):
	if isinstance(obj, Group):
		x = obj.get_x()
		y = obj.get_y()
		cx = obj.get_cx()
		cy = obj.get_cy()
		return f"""
				<p:grpSp>
					<p:nvGrpSpPr>
						<p:cNvPr name="{obj.name}" id="{obj.id}"/>
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
					</p:grpSpPr>"""+"\n".join(shape_to_pptx(shape) for shape in obj.shapes)+"""
				</p:grpSp>"""

	return f"""
			<p:sp>
				<p:nvSpPr>
					<p:cNvPr name="{obj.name}" id="{obj.id}"/>
					<p:cNvSpPr/>
					<p:nvPr/>
				</p:nvSpPr>
				<p:spPr>
					<a:xfrm>
						<a:off x="{obj.x}" y="{obj.y}"/>
						<a:ext cx="{obj.cx}" cy="{obj.cy}"/>
					</a:xfrm>
					<a:prstGeom prst="rect">
						<a:avLst/>
					</a:prstGeom>{style_to_pptx(obj.style)}
				</p:spPr>{text_to_pptx(obj.text)}
			</p:sp>"""