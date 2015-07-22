import os.path
import re
import requests
import json

import pprint

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

    if self.__replicate__ and self.__replicate__.has_key("library"):
      self.__library__ = self.__replicate__["library"]

    if self.__library__ and self.__library__.has_key("biosample"):
      self.__biosample__ = self.__library__["biosample"]

    if self.__biosample__:
      self.__biosample_term_id__ = self.__biosample__["biosample_term_id"]

    if not self.__biosample_term_id__:
      self.__biosample_term_id__ = self.__experiment__.get("biosample_term_id", None)


  def name(self):
    return self.__data__["@id"]

  def description(self):
    return self.__experiment__["description"]

  def epigenetic_mark(self, searched = None):
    if searched is None:
      searched = []

    if self.name() in searched:
      return None
    searched.append(self.name())

    if self.technique() == "RNA-seq":
      return "Transcriptome" ## TODO: Add to epigenetic mark

    if self.__epigenetic_mark__:
      return self.__epigenetic_mark__

    if self.__is_derived__:
      for d in self.__derived_from_id__:
        em = None
        if self.__shared_data__.has_key(d):
          em = self.__shared_data__[d].epigenetic_mark(searched)
        if em:
          return em

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
    return self.__experiment__["assay_term_name"]

  def biosample(self):
    if self.__biosample__:
      return self.__biosample__
    return {}

  def sample_data(self):
    pass

  def url(self):
    return self.__data__["href"]

  def format(self):
    return self.__data__["file_format"]

  def size(self):
    return self.__data__["file_size"]

  def extra_metadata(self):
    pass




class EncodeRepository(Repository):
  def __init__(self, proj, genome, path):
    super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed", "bigWig"], path)

  def __str__(self):
    return "<ENCODE Repository: [%s, %s]>" % (self.path, self.data_types)

  @property
  def index_path(self):
    """
    index_path is the path to the file which contains information of all datasets in the repository.
    """
    return None

  def read_datasets(self):
    new = 0
    epidb = PopulatorEpidbClient()

    file_types = ['bigWig', 'bed narrowPeak', 'bed broadPeak', 'bigBed broadPeak', 'bigBed narrowPeak', 'bigBed bedRnaElements', 'gtf', 'bed bedRnaElements', 'tsv', 'bigBed bedMethyl', 'bed bedMethyl', 'bigBed bedLogR', 'bigBed bed12', 'bed bed12', 'bigBed bedExonScore', 'bed bed9', 'bigBed bed9', 'bigBed peptideMapping']

    HEADERS = {'accept': 'application/json'}

    total = 0
    for file_type in file_types:
      payload["files.file_type"] = file_type
      response = requests.get(self.path+"/search", params=payload)
      print file_type, response.url
      response_json_dict = response.json()

      for experiment in response_json_dict["@graph"]:
        #print experiment

        total = self.process_encode_experiment(epidb, experiment["@id"])
        #self.process_encode_experiment("ENCSR973AYQ")

        """

          experiment = replicate.get("experiment", {})
          files = replicate.get("files", {})

          ds = Dataset(file["href"], file["file_format"], file, sample_id=sid)
          if self.add_dataset(ds):
            new += 1
            self.has_updates = True
        log.info("found %d new datasets in %s", new, self)
        """
    print total

  def process_encode_experiment(self, epidb, _id) :
    new = 0
    url = self.path + _id
    response = requests.get(url, params={'format':'json'})
    print response.url
    print response
    experiment = response.json()
    #pprint.pprint(experiment)
    experiment["description"]

    files = experiment["files"]
    r = 0
    d_total = 0

    shared_data = {}

    for f in files:
      #pprint.pprint(f)

      _id = f["@id"]
      derived_from_id = None

      if f.has_key("replicate"):
        #print f["href"], f["replicate"]["experiment"]["description"], f["replicate"]["experiment"]["target"]["label"]
        r += 1

      if f.has_key("derived_from"):
        #print f["href"], len(f["derived_from"]), f["derived_from"][0]["@id"]
        d_total += 1
        derived_from_id = [d["@id"] for d in f["derived_from"]]

      #if derived_from_id:
        #print _id, str(derived_from_id), _id in derived_from_id
      #print "derived_from_id: " + str(derived_from_id)

      ee = EncodeExperimentFile(f, experiment, derived_from_id, shared_data)
      shared_data[_id] = ee

    for k in shared_data.keys():
      file = shared_data[k]
      print file.name(), file.description(), file.epigenetic_mark(), file.technique(), file.url(), file.format(), file.size(), file.biosample_term_id()

      x = epidb.list_biosources({"ontology_id":file.biosample_term_id()})
      print x
      if len(x[1]) == 0:
        print "not found: ", file.biosample_term_id()
        ss = file.biosample()
        print ss.get("biosample_term_name", "not")
        print epidb.is_biosource("biosample_term_name")

      else:
        continue
        (status, (bs,)) = x
        (s, sid) = epidb.add_sample(bs[1], file.biosample() )
        print s, sid

        metadata = {"description": file.description(), "epigenetic_mark": file.epigenetic_mark(), "technique": file.technique(), "size": file.size()}
        ds = Dataset(file.url(), file.format(), metadata, sample_id=sid)
        if self.add_dataset(ds):
          new += 1
          self.has_updates = True

    #print len(files)
    #print r
    #print d_total
    """
    u'biosample_term_id': u'UBERON:0001049',
    u'biosample_term_name': u'neural tube',
    u'biosample_type': u'tissue',
    u'date_created': u'2015-06-09T20:45:27.136359+00:00',
    u'assay_term_name': u'ChIP-seq',
    u'developmental_slims': [u'ectoderm'],
    """


