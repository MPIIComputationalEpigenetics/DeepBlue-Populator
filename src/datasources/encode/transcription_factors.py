import requests

class EncodeTFs:
	def __init__(self, genome):
		self.__url__ = "https://www.encodeproject.org/search/?type=target&limit=all&format=json"
		specie = ""
		if genome.lower() in ["hg19", "grch38"]:
			specie = "Homo sapiens"

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

			for k in xrange(len(tf.get("investigated_as", []))):
				metadata["investigated_as_"+str(k)] = tf["investigated_as"][k]

			for k in xrange(len(tf["dbxref"])):
				metadata["dbxref_"+str(k)] = tf["dbxref"][k]

			metadata["organism"] = tf["organism"]["scientific_name"]
			if tf.has_key("gene_name"):
				metadata["gene_name"] = tf["gene_name"]

			self.__tfs__[tf["label"]] = metadata

	def __getitem__(self, tf_name):
		if not self.__tfs__:
			self.init()

		tf = self.__tfs__.get(tf_name, None)
		if not tf:
			return None

		return tf
