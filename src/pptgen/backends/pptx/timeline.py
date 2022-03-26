from pptgen.timeline import Timeline
from .animation import animation_to_pptx


def save_context(obj, context):
	seq_id = Timeline.get_id()
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
	if not obj.contexts[context]:
		result += f"""
								<p:par>
									<p:cTn id="{Timeline.get_id()}"/>
								</p:par>"""
	else:
		def add_group(result, group):
			return result + f"""
								<p:par>
									<p:cTn id="{Timeline.get_id()}" fill="hold">
										<p:stCondLst>
											<p:cond delay="indefinite"/>
											{"" if group[0].click else f'<p:cond delay="0" evt="onBegin"><p:tn val="{seq_id}"/></p:cond>'}
										</p:stCondLst>
										<p:childTnLst>

											<p:par>
												<p:cTn id="{Timeline.get_id()}" fill="hold">
													<p:stCondLst>
														<p:cond delay="0"/>
													</p:stCondLst>
													<p:childTnLst>"""+"".join(animation_to_pptx(animation) for animation in group)+"""
													</p:childTnLst>
												</p:cTn>
											</p:par>

										</p:childTnLst>
									</p:cTn>
								</p:par>"""
		group = [obj.contexts[context][0]]
		for animation in obj.contexts[context][1:]:
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


def timeline_to_pptx(obj):
	Timeline.reset_id()
	return f"""
	<p:timing>
		<p:tnLst>
			<p:par>
				<p:cTn id="{Timeline.get_id()}" nodeType="tmRoot" restart="never" dur="indefinite">
					<p:childTnLst>"""+"".join(save_context(obj, context) for context in obj.contexts)+"""
					</p:childTnLst>
				</p:cTn>
			</p:par>
		</p:tnLst>
	</p:timing>"""