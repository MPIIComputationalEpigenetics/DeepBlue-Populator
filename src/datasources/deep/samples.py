import codecs
import os
import xmlrpclib

SAMPLE_METADATA_DIRECTORY = "../data/deep/metadata/sample/"

class Sample:
  def __init__(self, data):
    self._data = data
    self._data["source"] = "DEEP"
    self._biosource = None

  def id(self):
    return self._data["DEEP_SAMPLE_ID"]

  def biosource(self):
    if self._biosource:
      return self._biosource

    biomaterial_type = self._data['BIOMATERIAL_TYPE'].lower()
    if biomaterial_type == 'cell culture':
      self._biosource = self._data["LINE"]

    elif biomaterial_type == 'primary tissue':
      self._biosource = self._data["TISSUE_TYPE"]

    elif biomaterial_type == 'primary cell':
      self._biosource = self._data["CELL_TYPE"]

    elif biomaterial_type == 'primary cell culture':
      self._biosource = self._data["CELL_TYPE"]

    else:
      self._biosource = "Invalid Biosource, biomateril: " + self._data['BIOMATERIAL_TYPE']

    return self._biosource

  def set_biosource(self, biosource):
    self._biosource = biosource

  def is_organism(self, organism):
    return self._data["ORGANISM"].lower() == organism.lower()

  def data(self):
    return self._data;


def process_metadata(file_location):
  data = {}

  # Check the encoding
  try:
    f = codecs.open(file_location, encoding='utf-16')
    f.readlines()
    f = codecs.open(file_location, encoding='utf-16')
  except UnicodeError as e:
    f = codecs.open(file_location, encoding='utf-8')

  for l in f.readlines():
    l = l.strip()
    if not l:
      continue
    s = l.split("\t", 1)
    if (len(s) == 2) :
      data[s[0]] = s[1]
    elif (len(s) == 1):
      data[s[0]] = "-"
  return data

class DeepSamples:
  def __init__(self, deepblue, deep_xmlrpc_server):
    self._epidb = deepblue
    self._srv = xmlrpclib.Server(deep_xmlrpc_server)

  def process(self):
    deep_samples = []
    samples = self._srv.get_files_by_type('Sample')
    for s in samples[1]["p_iofiles_col"]:
      if s["active"] == "N": continue
      s["filepath"] = SAMPLE_METADATA_DIRECTORY
      sample_location = os.path.join(s["filepath"], s["filename"])
      sample = Sample(process_metadata(sample_location))

      if sample.biosource() == "naive CD4-positive T cell":
        sample.set_biosource("naive thymus-derived CD4-positive, alpha-beta T cell")
      if sample.biosource() == 'Effector memory CD4-positive T cell, terminally differentiated (TEMRA)':
        sample.set_biosource("effector CD4-positive, alpha-beta T cell")

      bs = sample.biosource()
      s, b = self._epidb.is_biosource(bs)
      if (s == "error"):
        print s, b
        continue

      deep_samples.append(sample)
    return deep_samples
