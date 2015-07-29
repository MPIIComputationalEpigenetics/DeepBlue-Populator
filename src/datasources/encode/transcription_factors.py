import requests

class EncodeTFs:
	def __init__(self, specie):
		self.__url__ = "https://www.encodeproject.org/search/?type=target&investigated_as=transcription%20factor&limit=all&format=json"
		self.__specie__ = specie
		self.__tfs__ = {}

	def init(self):
		payload = {}
		payload["organism.scientific_name"] = self.__specie__
		response = requests.get(self.__url__, params=payload)
		experiment = response.json()
		tfs = experiment["@graph"]

		self.__tfs__ = {}
		for tf in tfs:
			metadata = {}
			metadata["encode_id"] = tf["@id"]

			for k in xrange(len(tf["dbxref"])):
				metadata["dbxref_"+str(k)] = tf["dbxref"][k]

			metadata["organism"] = tf["organism"]["scientific_name"]
			metadata["gene_name"] = tf["gene_name"]

			self.__tfs__[tf["label"]] = metadata

	def __getitem__(self, tf_name):
		if not self.__tfs__:
			self.init()

		tf = self.__tfs__.get(tf_name, None)
		if not tf:
			return None

		return tf
