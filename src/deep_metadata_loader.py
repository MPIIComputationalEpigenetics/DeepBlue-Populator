import xmlrpclib
import os
import codecs

srv = xmlrpclib.Server('http://deep01.mpi-inf.mpg.de:50005')
deepblue = xmlrpclib.Server("http://deepblue.mpi-inf.mpg.de/xmlrpc")
user_key = "Ty3ArObJhuWK9MOy"
print deepblue.echo(user_key)


samples = srv.get_files_by_type('Sample')

class Sample:
  def __init__(self, data):
    self._data = data

  def biosource(self):
    biomaterial_type = self._data['BIOMATERIAL_TYPE'].lower()
    if biomaterial_type == 'cell culture':
      return self._data["LINE"]

    elif biomaterial_type == 'primary tissue':
      return self._data["TISSUE_TYPE"]

    elif biomaterial_type == 'primary cell':
      return self._data["CELL_TYPE"]

    elif biomaterial_type == 'primary cell culture':
      return self._data["CELL_TYPE"]

    else:
      print self._data
      print self._data['BIOMATERIAL_TYPE']

def process_sample(file_location):
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


for s in samples[1]["p_iofiles_col"]:
  if s["active"] == "N":
    continue

  s["filepath"] = "/Users/albrecht/mpi/DeepBlue-Populator/data/deep/metadata/sample/"
  sample_location = os.path.join(s["filepath"], s["filename"])

  sample = Sample(process_sample(sample_location))

  bs = sample.biosource()
  s, b = deepblue.is_biosource(bs, user_key)
  if (s == "error"):
    print bs

