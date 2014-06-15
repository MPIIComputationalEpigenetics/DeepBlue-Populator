class Annotation:
	def __init__(self, props):
		self.props = props

	@property
	def name(self):
		return self.props["name"]

	@property
	def genome(self):
	    return self.props["genome"]

	@property
	def description(self):
	    return self.props["description"]

	@property
	def data_file(self):
	    return self.props["data_file"]

	@property
	def file_format(self):
	    return self.props["file_format"]

	@property
	def extra_metadata(self):
		if self.props.has_key("extra_metadata"):
			return self.props["extra_metadata"]
		else:
			return {}