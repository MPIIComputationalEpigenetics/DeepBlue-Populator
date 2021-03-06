import codecs
import ConfigParser
import os
import pprint
import re
import subprocess
import xmlrpclib

from dataset import Dataset
from epidb_interaction import PopulatorEpidbClient
from repository import Repository
from settings import DEEP_XMLRPC_SERVER
from datasources.deep.controlled_vocabularies import *
from datasources.deep.samples import DeepSamples

def process_metadata(file_location):
  data = {}

  # Check the encoding
  try:
    f = codecs.open(file_location, encoding='utf-16')
    f.readlines()
    f = codecs.open(file_location, encoding='utf-16')
  except UnicodeError as e:
    try:
      f = codecs.open(file_location, encoding='utf-8')
      f.readlines()
      f = codecs.open(file_location, encoding='utf-8')
    except UnicodeError as e:
      f = codecs.open(file_location, encoding='latin-1')

  for l in f.readlines():
    l = l.strip()
    if not l:
      continue
    s = l.split("\t", 1)
    if (len(s) == 2) :
      data[s[0]] = s[1]
  return data

def file_to_type(file_name):
  _sub, extension = os.path.splitext(file_name)
  if extension == ".gz":
    _sub, extension = os.path.splitext(_sub)

  extension = extension.lower()
  if extension == ".bw":
    return "bigWig"
  if extension == ".bed":
    return "bed"
  if extension == ".broadpeak":
    return "broadPeak"
  if extension == ".narrowpeak":
    return "narrowPeak"
  if extension == ".bedgraph":
    return "bedgraph"
  if extension == ".fpkm_tracking" and "_genes" in file_name:
    return "cufflinks_fpkm_genes"
  if extension == ".fpkm_tracking" and "_isoforms" in file_name:
    return "cufflinks_fpkm_isoforms"

  else:
    print "unknow", extension

class Experiment:
  def __init__(self, data):
    self._data = data

  def data(self):
    return self._data

class DeepRepository(Repository):
  def __init__(self, proj, genome, path):
    super(DeepRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed", "bigWig", "bedgraph", "cufflinks_fpkm_genes"], path)
    self._samples = {}
    if genome == "hs37d5" or genome == "GRCh38":
      self.organism = "homo sapiens"
    elif genome == "GRCm38":
      self.organism = "mus musculus"
    else:
      print "Unknow genome", genome

  def __str__(self):
    return "<DEEP Repository: [%s, %s, %s]>" % (self.genome, self.path, self.data_types)

  def read_datasets(self):
    file_types = ['signal', 'region', 'FPKM estimates']

    new = 0

    deepblue_sample = {}
    experiment_metadata_collection = {}

    epidb = PopulatorEpidbClient()
    samples = DeepSamples(epidb, DEEP_XMLRPC_SERVER)
    samples = samples.process()

    EXPERIMENT_METADATA_DIRECTORY = "../data/deep/metadata/experiment/"


    config = ConfigParser.ConfigParser()
    config.read("../data/deep/deep_generic_re_python2.ini")
    deep_sample_id_pattern = re.compile(config.get("DEEPsample", "deep_id"))
    deep_cl_id_pattern = re.compile(config.get("DEEPcline", "deep_id"))

    srv = xmlrpclib.Server(DEEP_XMLRPC_SERVER)

    for sample in [s for s in samples if s.is_organism(self.organism)] :
      biosource = sample.biosource()
      if biosource == "Naive CD4-positive T cell":
        biosource = "CD4-positive, alpha-beta T cell"
      elif biosource == "white adipose":
        biosource = "white adipose tissue"

      (s, s_id) = epidb.add_sample(biosource, sample.data())
      deepblue_sample[sample.id()] = s_id

      sample_experiments_metadata = srv.get_files_by_type("Experiment", sample.id())
      for experiment_metadata_info in sample_experiments_metadata[1]["p_iofiles_col"]:
        file_path = experiment_metadata_info["filepath"]
        experiment_sample_id = os.path.basename(os.path.normpath(file_path))
        experiment_emd_path = os.path.join(EXPERIMENT_METADATA_DIRECTORY, experiment_sample_id, experiment_metadata_info["filename"])
        experiment_emd_key = experiment_metadata_info["filename"][:-8] # remove _emd.csv
        if not os.path.exists(experiment_emd_path):
          print "Path: " + experiment_emd_path + " does not exists."
          continue
        experiment = Experiment(process_metadata(experiment_emd_path))
        experiment_metadata_collection[experiment_emd_key] = experiment

      for type_ in file_types:
        files = srv.get_files_by_type(type_, sample.id())

        for file_info in files[1]["p_iofiles_col"]:
          file_name = file_info["filename"]
          experiment_data_file_path = os.path.join(file_info["filepath"], file_info["filename"])

          experiment_genome = None
          if "GRCh37" in experiment_data_file_path:
            experiment_genome = "hs37d5"
          elif "GRCh38" in experiment_data_file_path:
            experiment_genome = "GRCh38"
          elif "GRCm38" in experiment_data_file_path:
            experiment_genome = "GRCm38"

          track_hub = re.compile("\.THBv\d\.")
          if re.search(track_hub, file_name): # Ignore Track Hub files
            continue

          log2Input = re.compile("-log2-Input")
          if re.search(log2Input, file_name):
            file_name = file_name.replace("-log2-Input", "")

          exp_name = os.path.splitext(file_name)[0].split(".")[0]
          if not experiment_metadata_collection.has_key(exp_name):
            print "Experiment metadata not found:", exp_name
            emd = {"WARNING": "Metadata for this experiment was not found."}
          else:
            emd = experiment_metadata_collection[exp_name].data()

          res = re.match(deep_sample_id_pattern, file_name)
          if not res:
            res = re.match(deep_cl_id_pattern, file_name)
            if not res:
              print file_name, " not matched with the sample or cell line regular expressions"
              continue

          DEEPID = res.group("DEEPID")
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

          experiment_metadata = {}
          experiment_metadata["GENOME"] = experiment_genome
          experiment_metadata["DEEPID"] = DEEPID
          experiment_metadata["SAMPLEID"] = SAMPLEID
          experiment_metadata["SUBPROJECT"] = get_subproject(SUBPROJECT)
          experiment_metadata["ORGAN_TISSUE"] = get_organ_tissue(ORGAN)
          experiment_metadata["CELLTYPE"] = get_celltype(CELLTYPE)
          experiment_metadata["STATUS"] = get_disease_status(STATUS)
          experiment_metadata["EPIGENETIC_MARK"] = get_epigenetic_mark_technology(LIBRARY)[0]
          experiment_metadata["TECHNOLOGY"] = get_epigenetic_mark_technology(LIBRARY)[1]
          experiment_metadata["SEQCENTER"] = get_sequencing_center(SEQCENTER)
          experiment_metadata["REPNUM"] = REPNUM
          experiment_metadata["extra"] = emd
          experiment_metadata["location"] = experiment_data_file_path

          file_type = file_to_type(file_name)

          ds = Dataset(experiment_data_file_path, file_type, experiment_metadata, sample_id=deepblue_sample[sample.id()])
          if self.add_dataset(ds):
            new += 1
            self.has_updates = True
