import os.path
import re
import requests
import json

from threading import Thread
from Queue import Queue

from datasources.encode.vocabulary import antibodyToTarget
from epidb_interaction import PopulatorEpidbClient

from dataset import Dataset
from log import log
from repository import Repository


"""
A Repository refers to a source of datasets belonging to a certain project.
It detects the available datasets in the repository and can coordinate their
retrival and processing.
"""

# Insert samples
# Get size
# Put the entire line in the extra_metadata !

"""
payload = {'assembly': 'hg19',
           'type': 'experiment',
           'status': 'released',
           'frame':'embedded',
           'format':'json'}


https://www.encodeproject.org/search/?type=experiment&status=released&assembly=hg19&files.file_type=bigWig&files.file_type=bed%20narrowPeak&files.file_type=bed%20broadPeak&files.file_type=bigBed%20broadPeak&files.file_type=bigBed%20narrowPeak&files.file_type=bigBed%20bedRnaElements&files.file_type=gtf&files.file_type=bed%20bedRnaElements&files.file_type=tsv&files.file_type=bigBed%20bedMethyl&files.file_type=bed%20bedMethyl&files.file_type=bigBed%20bedLogR&files.file_type=bigBed%20bed12&files.file_type=bed%20bed12&files.file_type=bigBed%20bedExonScore&files.file_type=bed%20bed9&files.file_type=bigBed%20bed9&files.file_type=bigBed%20peptideMapping&limit=all

"""

payload = {'type': 'experiment',
           'status': 'released',
           'frame':'object', # embedded
           'format':'json',
           'limit': 'all'}

class EncodeExperimentFile:
  def __init__(self, data, experiment, derived_from_id, shared_data):
    self.__data__ = data
    self.__experiment__ = experiment
    self.__derived_from_id__ = derived_from_id
    self.__shared_data__ = shared_data
    self.__is_derived__ = derived_from_id != None

    self.__replicate__ = None
    self.__target__ = None
    self.__epigenetic_mark__ = None
    self.__library__ = None
    self.__biosample__ = None

    self.__biosample_term_id__ = None

    self.__replicate__ = data.get("replicate", None)

    if self.__replicate__:
      self.__experiment__ = self.__replicate__.get("experiment", None)

    if self.__experiment__:
        self.__target__ = self.__experiment__.get("target", None)

    if self.__target__:
      self.__epigenetic_mark__ = self.__target__.get("label", None)
      tf = antibodyToTarget(self.__epigenetic_mark__)
      if tf:
        self.__epigenetic_mark__ = tf

    if self.__replicate__ and self.__replicate__.has_key("library"):
      self.__library__ = self.__replicate__["library"]

    if self.__library__ and self.__library__.has_key("biosample"):
      self.__biosample__ = self.__library__["biosample"]

    if self.__biosample__:
      self.__biosample_term_id__ = self.__biosample__["biosample_term_id"]

    if not self.__biosample_term_id__:
      self.__biosample_term_id__ = self.__experiment__.get("biosample_term_id", None)

    if self.__biosample_term_id__ == "NTR:0000837": ## from NTR to EFO for H7-hESC
      self.__biosample_term_id__ = "EFO:0005904"

    if self.__biosample_term_id__ == "NTR:0000961":
      self.__biosample_term_id__ = "EFO:0005913"

    if self.__biosample_term_id__ == "NTR:0000735":
      self.__biosample_term_id__ = "EFO:0005909"

    if self.__biosample_term_id__ == "EFO:0002114": # http://www.ebi.ac.uk/efo/EFO_0002114 - BE2C
      self.__biosample_term_id__ = "EFO:0005725" # http://www.ebi.ac.uk/efo/EFO_0005725 - BE(2)-C

    if self.__biosample_term_id__ == "CL:0002539": # http://www.ebi.ac.uk/ontology-lookup/?termId=CL:0002539 - aortic smooth muscle cell
      self.__biosample_term_id__ = "EFO:0002775"


  def name(self):
    return self.__data__["@id"]

  def description(self):
    return self.__experiment__.get("description", "")

  def epigenetic_mark(self, searched = None):
    if searched is None:
      searched = []

    if self.name() in searched:
      return None
    searched.append(self.name())

    if self.technique() == "RNA-seq":
      return "RNA"

    if self.__epigenetic_mark__:
      return self.__epigenetic_mark__

    if self.__is_derived__:
      for d in self.__derived_from_id__:
        em = None
        if self.__shared_data__.has_key(d):
          em = self.__shared_data__[d].epigenetic_mark(searched)
        if em:
          return em

    if self.technique() == "FAIRE-seq":
      return "Regulatory Elements"

    if self.technique() == "CAGE":
      return "mRNA"

    if self.technique() == "DNase-seq":
      return "DNaseI"

    if self.technique() == "WGSBS":
      return "DNA Methylation"

    if self.technique() == "RRBS":
      return "DN Methylation"

    if self.technique() == "5C":
      return "Chromosome conformation capture"

    if self.technique() == "RNA profiling by array assay":
      return "Gene Expression"

    return None

  def biosample_term_id(self, searched = None):
    if searched is None:
      searched = []

    if self.name() in searched:
      return None
    searched.append(self.name())

    if self.__biosample_term_id__:
      return self.__biosample_term_id__

    if self.__is_derived__:
      for d in self.__derived_from_id__:
        ti = None
        if self.__shared_data__.has_key(d):
          ti = self.__shared_data__[d].biosample_term_id(searched)
        if ti:
          return ti

    return None

  def technique(self):
    assay_term_name = self.__experiment__["assay_term_name"]

    if assay_term_name == "whole-genome shotgun bisulfite sequencing":
      return "WGSBS"

    return assay_term_name

  def biosample(self):
    if self.__biosample__:
      return self.__biosample__
    return {}

  def url(self):
    return "https://www.encodeproject.org" + self.__data__["href"]

  def format(self):
    return self.__data__["file_format"]

  def size(self):
    return self.__data__["file_size"]

  def extra_metadata(self):
    emd = {}
    emd["encode_accession"] = self.__experiment__["accession"]
    emd["status"] = self.__experiment__["status"]
    emd["original_file_size"] = self.size()
    emd["original_file_url"] = self.url()

    emd["output_category"] = self.__data__["output_category"]

    emd["file_url"] = "https://www.encodeproject.org" + self.__data__["@id"]
    emd["experiment_url"] = "https://www.encodeproject.org" + self.__experiment__["@id"]

    lab = self.__experiment__.get("lab", {})
    for k in lab.keys():
      value = lab[k]
      if isinstance(value, basestring):
        emd["lab_"+k] = lab[k]

    if self.__replicate__:
      for r in ["biological_replicate_number", "technical_replicate_number"]:
        if self.__replicate__.has_key(r):
          emd[r] = self.__replicate__[r]

    return emd



class EncodeRepository(Repository):
  def __init__(self, proj, genome, path):
    #super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed", "bigWig"], path)
    super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed"], path)
    self.q = None

  def __str__(self):
    return "<ENCODE Repository: [%s, %s]>" % (self.path, self.data_types)

  def worker(self):
    while True:
        item = self.q.get()
        self.process_encode_experiment(item)
        self.q.task_done()

  @property
  def index_path(self):
    """
    index_path is the path to the file which contains information of all datasets in the repository.
    """
    return None

  def read_datasets(self):
    self.q = Queue()
    new = 0

    for i in xrange(32):
      t = Thread(target=self.worker)
      t.daemon = True
      t.start()

    file_types = ['bigWig', 'bed narrowPeak', 'bed broadPeak', 'bigBed broadPeak', 'bigBed narrowPeak', 'bigBed bedRnaElements', 'gtf', 'bed bedRnaElements', 'tsv', 'bigBed bedMethyl', 'bed bedMethyl', 'bigBed bedLogR', 'bigBed bed12', 'bed bed12', 'bigBed bedExonScore', 'bed bed9', 'bigBed bed9', 'bigBed peptideMapping']

    HEADERS = {'accept': 'application/json'}

    enqueued_experiments = []

    for file_type in file_types:
      payload["files.file_type"] = file_type
      payload["replicates.library.biosample.donor.organism.scientific_name"] = self.genome
      response = requests.get(self.path+"/search", params=payload)
      response_json_dict = response.json()

      for experiment in response_json_dict["@graph"]:
        experiment_id = experiment["@id"]
        if not experiment_id in enqueued_experiments:
          self.q.put(experiment_id)
          enqueued_experiments.append(experiment_id)

    self.q.join()

  def process_encode_experiment(self, experiment_id) :
    epidb = PopulatorEpidbClient()
    new = 0
    url = self.path + experiment_id
    response = requests.get(url, params={'format':'json'})
    #log.info("%s %s", response.url, response)
    experiment = response.json()

    files = experiment["files"]

    shared_data = {}

    for f in files:
      _id = f["@id"]
      derived_from_id = None

      if f.has_key("derived_from"):
        derived_from_id = [d["@id"] for d in f["derived_from"]]

      ee = EncodeExperimentFile(f, experiment, derived_from_id, shared_data)
      shared_data[_id] = ee

    for k in shared_data.keys():
      file = shared_data[k]

      if file.technique() == "Repli-chip": # This track shows genome-wide assessment of DNA replication timing in cell lines using NimbleGen tiling CGH microarrays.
        continue

      if file.technique() == "Repli-seq": # DNA replication timing by sequencing assay
        continue

      if file.technique() == "RNA-PET":
        continue

      if file.technique() == "protein sequencing by tandem mass spectrometry assay":
        continue

      if file.technique() == "comparative genomic hybridization by array":
        continue

      if file.technique() == "MNase-seq":
        continue

      if file.name() is None or file.epigenetic_mark() is None or file.technique() is None or file.url() is None or file.format() is None or file.biosample_term_id() is None:
        log.error("File from experiment id %s - %s %s  not included because it does not have all necessary information.\nepigenetic mark: %s\ntechnique: %s\nurl: %s\nformat: %s\nbiosample: %s.", experiment_id, file.name(), file.description(), file.epigenetic_mark(), file.technique(), file.url(), file.format(), file.biosample_term_id())
        continue


      biosurce_info = epidb.list_biosources({"ontology_id":file.biosample_term_id()})
      biosource_similar = ""
      biosource = ""

      if len(biosurce_info[1]) == 0:
        ss = file.biosample()
        biosample_term_name = ss.get("biosample_term_name", "")
        (s, biosource_similar) = epidb.is_biosource(biosample_term_name)

        if s == "okay":
          biosource = biosource_similar[0]
        else:
          if not biosample_term_name:
            log.error("ontology term ID not found: %s (no biosample name was define)", file.biosample_term_id())
          else:
            log.error("ontology term ID not found: %s (%s - %s)", file.biosample_term_id(), biosample_term_name, s)
          continue

      if len(biosurce_info[1]) == 1:
        (status, (biosource,)) = biosurce_info
        biosource = biosource[1]

      (s, sid) = epidb.add_sample(biosource, file.biosample() )

      metadata = {"description": file.description(), "epigenetic_mark": file.epigenetic_mark(), "technique": file.technique(),  "extra_metadata": file.extra_metadata()}
      ds = Dataset(file.url(), file.format(), metadata, sample_id=sid)
      if self.add_dataset(ds):
        new += 1
        self.has_updates = True
