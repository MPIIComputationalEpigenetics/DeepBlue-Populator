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
	def data_location(self):
		if self.local:
			return self.props["data_file"]
		else:
			return self.props["data_url"]

	@property
	def file_format(self):
	    return self.props["file_format"]

	@property
	def extra_metadata(self):
		if self.props.has_key("extra_metadata"):
			return self.props["extra_metadata"]
		else:
			return {}

	@property
	def local(self):
	    return self.props.has_key("data_file")
