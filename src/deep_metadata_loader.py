import re
import xmlrpclib
import os
import codecs
import subprocess
import ConfigParser


srv = xmlrpclib.Server('http://deep01.mpi-inf.mpg.de:50005')
deepblue = xmlrpclib.Server("http://deepblue.mpi-inf.mpg.de/xmlrpc")
user_key = "Ty3ArObJhuWK9MOy"

ssh_server = "infcontact1"
ssh_user = "albrecht"
ssh_download = "download/"

SAMPLE_METADATA_DIRECTORY = "../data/deep/metadata/sample/"
EXPERIMENT_METADATA_DIRECTORY = "../data/deep/metadata/experiment/"

file_types = ['signal', 'region']

config = ConfigParser.ConfigParser()
config.read("../data/deep/deep_generic_re_python2.ini")
deep_id_string = config.get("DEEPsample", "deep_id")
deep_id_pattern = re.compile(deep_id_string)

experiment_metadata = {}

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

  def data(self):
    return self._data;

class Experiment:
  def __init__(self, data):
    self._data = data

  def data(self):
    return self._data


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


for s in samples[1]["p_iofiles_col"]:
  if s["active"] == "N":
    continue

  s["filepath"] = SAMPLE_METADATA_DIRECTORY
  sample_location = os.path.join(s["filepath"], s["filename"])

  sample = Sample(process_metadata(sample_location))

  bs = sample.biosource()
  s, b = deepblue.is_biosource(bs, user_key)
  if (s == "error"):
    print bs
    continue

  deep_sample_id = sample.data()["DEEP_SAMPLE_ID"]

  sample_experiments_metadata = srv.get_files_by_type("Experiment", deep_sample_id)
  for experiment_metadata_info in sample_experiments_metadata[1]["p_iofiles_col"]:
    #print experiment_metadata_info

    file_path = experiment_metadata_info["filepath"]
    base_path = os.path.basename(os.path.normpath(file_path))

    experiment_sample_path = os.path.join(EXPERIMENT_METADATA_DIRECTORY, base_path, experiment_metadata_info["filename"])

    experiment = Experiment(process_metadata(experiment_sample_path))
    experiment_metadata[base_path] = experiment

  for type in file_types:
    files = srv.get_files_by_type(type, deep_sample_id)

    for file_info in files[1]["p_iofiles_col"]:
      #print file_info
      file_name = file_info["filename"]
      #print os.path.splitext(file_name)
      file = file_info["filepath"] + file_info["filename"]
      scp_command = "scp " + ssh_user+"@"+ssh_server+file+" "+ssh_download
      #print scp_command
      #subprocess.Popen(["scp", "%s@%s:%s" % (ssh_user, ssh_server, file), "%s" % (ssh_download)]).wait()

      res = re.match(deep_id_pattern, file_name)
      if not res:
        continue

      SAMPLEID = res.group('SAMPLEID')
      DONORID = res.group('DONORID')
      SUBPROJECT = res.group('SUBPROJECT')
      DONOR = res.group('DONOR')
      ORGAN = res.group('ORGAN')
      CELLTYPE = res.group('CELLTYPE')
      STATUS = res.group("STATUS")
      LIBRARY = res.group('LIBRARY')
      SEQCENTER = res.group('SEQCENTER')
      REPNUM = res.group('REPNUM')

      print "-" * 30
      print DEEPID
      print SAMPLEID
      print DONORID
      print SUBPROJECT
      print DONOR
      print ORGAN
      print CELLTYPE
      print STATUS
      print LIBRARY
      print SEQCENTER
      print REPNUM
      print "-" * 30










