class Timeline:
	id = 0
	def reset_id():
		Timeline.id = 0
	def get_id():
		Timeline.id += 1
		return Timeline.id

	def __init__(self, *animations):
		self.contexts = {"main":animations}

	def add(self, *animations, on=None):
		if on is None:
			self.contexts["main"].extend(animations)
		elif on in self.contexts:
			self.contexts[on.id].extend(animations)
		else:
			self.contexts[on.id] = animations

	def save_context(self, context):
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
		if not self.contexts[context]:
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
													<p:childTnLst>"""+"".join(animation.save() for animation in group)+"""
													</p:childTnLst>
												</p:cTn>
											</p:par>

										</p:childTnLst>
									</p:cTn>
								</p:par>"""
			group = [self.contexts[context][0]]
			for animation in self.contexts[context][1:]:
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

	def save(self):
		Timeline.reset_id()
		return f"""
	<p:timing>
		<p:tnLst>
			<p:par>
				<p:cTn id="{Timeline.get_id()}" nodeType="tmRoot" restart="never" dur="indefinite">
					<p:childTnLst>"""+"".join(self.save_context(context) for context in self.contexts)+"""
					</p:childTnLst>
				</p:cTn>
			</p:par>
		</p:tnLst>
	</p:timing>"""