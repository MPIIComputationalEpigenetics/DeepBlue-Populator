import os.path
import re
import requests
import json
import collections

from threading import Thread
from Queue import Queue

from datasources.encode.vocabulary import antibodyToTarget
from datasources.encode.transcription_factors import EncodeTFs
from epidb_interaction import PopulatorEpidbClient

from dataset import Dataset
from log import log
from repository import Repository

import flatdict

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

    if self.__experiment__:
        self.__target__ = self.__experiment__.get("target", None)

    if self.__target__:
      self.__epigenetic_mark__ = self.__target__.get("label", None)

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

    if self.__biosample_term_id__ == "NTR:0001510": # ES-E14
      self.__biosample_term_id__ = "EFO:0003074" # Mouse embryonic stem cell line

    if self.__biosample_term_id__ == "NTR:0000741": # splenic B cell (not defined in any of ours ontology)
      self.__biosample_term_id__ = "CL:0000236" # B Cell

    if self.__biosample_term_id__ == "NTR:0001510": # (ES-E14 - error)
      self.__biosample_term_id__ = "EFO:0003074"

    if self.__biosample_term_id__ == "NTR:0001521": # "ZHBTc4-mESC",
      self.__biosample_term_id__ = "EFO:0005914"

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
      return "DNA Methylation"

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

  def process_biosample(self, bs):
    flat = flatdict.FlatDict(bs, delimiter=":").as_dict()
    flat_bs = {}
    for k in flat.keys():
      if flat[k]:
        if isinstance(flat[k], list):
          for p in range(len(flat[k])):
            flat_bs[k+":"+str(p)] = flat[k][p]
        else:
          flat_bs[k] = flat[k]
    return flat_bs

  def biosample(self, searched = None):
    if searched is None:
      searched = []

    if self.name() in searched:
      return {}

    searched.append(self.name())

    # If the file has biosample
    if self.__biosample__:
      return self.process_biosample(self.__biosample__)

    # If the file that it does derive
    if self.__is_derived__:
      for d in self.__derived_from_id__:
        ti = None
        if self.__shared_data__.has_key(d):
          ti = self.__shared_data__[d].biosample(searched)
        if ti:
          return ti

    # get biosample from
    replicates = self.__experiment__.get("replicates", None)
    s = "from experiment"
    if replicates and len(replicates) > 0:
      s = "unicode"
      if not isinstance(replicates[0], unicode):
        s = "replicates"
        library = replicates[0].get("library", None)
        if library:
          s = "library"
          biosample = library.get("biosample", {})
          s = "biosamples"
          if biosample:
            return self.process_biosample(biosample)

    print s

    s = "from files"
    # get biosample from the files of the same experiment
    import pprint
    pprint.pprint( self.__experiment__)
    for f in self.__experiment__.get("files"):
      print "file unicode"
      if not isinstance(f, unicode):
        replicate = f.get("replicate")
        if replicate:
          s = "replicate unicode"
          if not isinstance(replicates[0], unicode):
              print "library"
              library = replicate.get("library")
              if library:
                biosample = library.get("biosample")
                print "biosamples"
                if biosample:
                  return self.process_biosample(biosample)

    print s

    return {}


  def url(self):
    return "https://www.encodeproject.org" + self.__data__["href"]

  def format(self):
    return self.__data__["file_format"]

  def file_type(self):
    return self.__data__["file_type"]

  def size(self):
    return self.__data__["file_size"]

  def extra_metadata(self):
    emd = {}
    emd["file_encode_accession"] = self.__data__["accession"]
    emd["experiment_encode_accession"] = self.__experiment__["@id"]
    emd["experiment_url"] = "https://www.encodeproject.org" + self.__experiment__["@id"]

    emd["status"] = self.__experiment__["status"]
    emd["original_file_size"] = self.size()
    emd["original_file_url"] = self.url()

    emd["output_category"] = self.__data__["output_category"]

    emd["file_url"] = "https://www.encodeproject.org" + self.__data__["@id"]

    emd["file_type"] = self.file_type()
    if self.__data__.has_key("submitted_file_name"):
      emd["submitted_file_name"] = self.__data__["submitted_file_name"]

    if self.__data__.has_key("output_type"):
      emd["output_type"] = self.__data__["output_type"]

    assembly = self.__data__.get("assembly", None)
    if not assembly:
      assembly = self.__experiment__.get("assembly", None)
      if len(assembly) > 0:
        assembly = assembly[0]
      else:
          log.error("Assembly not found for %s", self.__data__["@id"])
          return None

    emd["assembly"] = assembly

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
    super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed", "bigWig"], path)
    #super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed"], path)
    self.epigenetic_marks = None
    self.q = None
    self.encode_tfs = EncodeTFs(genome)

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

  def check_target(self, target_name):
    epidb = PopulatorEpidbClient()

    if not self.epigenetic_marks:
      (s, ems) = epidb.list_epigenetic_marks()
      self.epigenetic_marks = [em[1] for em in ems]

    if target_name not in self.epigenetic_marks:
      log.info("it is not in " + target_name)
      tf_metadata = self.encode_tfs[target_name]
      if not tf_metadata:
        log.error("Metadata for " + target_name + " not found")
        return

      (s, em) = epidb.add_epigenetic_mark(target_name, str(tf_metadata))
      if (s == "okay"):
        self.epigenetic_marks.append(target_name)
      else:
        log.error("Still missing %s %s", target_name, em)

  def process_encode_experiment(self, experiment_id) :
    epidb = PopulatorEpidbClient()
    new = 0
    url = self.path + experiment_id
    response = requests.get(url, params={'format':'json'})
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

      if file.technique() == "ChIA-PET":
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

      if not file.biosample():
        import pprint
        print file.name(), experiment_id, file.format()
        pprint.pprint(file.biosample())

      (s, sid) = epidb.add_sample(biosource, file.biosample() )

      self.check_target(file.epigenetic_mark())

      if not file.extra_metadata():
        continue

      metadata = {"description": file.description(), "epigenetic_mark": file.epigenetic_mark(), "technique": file.technique(),  "extra_metadata": file.extra_metadata()}
      ds = Dataset(file.url(), file.format(), metadata, sample_id=sid)
      if self.add_dataset(ds):
        new += 1
        self.has_updates = True
