import os.path
import re
import urllib
import util
import traceback
import threading

from dataset import Dataset
from settings import mdb, log, max_threads
from repository import Repository

"""
A Repository refers to a source of datasets belonging to a certain project.
It detects the available datasets in the repository and can coordinate their
retrival and processing.
"""
class EncodeRepository(Repository):

  def __init__(self, proj, genome, path, user_key):
    super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed"], path, user_key)

  def __str__(self):
    return "<ENCODE Repository: [%s, %s]>" % (self.path, self.data_types)

  """
  index_path is the path to the file which contains information of all
  datasets in the repository.
  """
  @property
  def index_path(self):
    return os.path.join(self.path, "files.txt")

  @property
  def id(self):
    idl = mdb.repositories.find_one({
      "project": self.project, "path": self.path}, ["_id"])
    if not idl:
      return None
    return idl["_id"]

  """
  read_datasets analyses the repositorie's index file and flags
  new datasets.
  """
  def read_datasets(self):
    epigeneticMark = None

    new = 0
    f = urllib.urlopen(self.index_path)
    for line in f:
      s = line.strip().split(None, 1)
      file_name, meta_s = s[0], s[1]

      meta = {}
      for kv in meta_s.split("; "):
        fs = kv.split("=")
        meta[fs[0]] = fs[1]

      if not meta.has_key("dataType"):
        log.info("Line %s from %s does not have datatype" %(line, self.path))
        continue

      r = re.findall('[A-Z][a-z]*', meta["composite"])

      em = r[-1]
      if r[-2] not in ["Haib", "Sydh", "Broad", "Uw", "Uchicago"]:
        em = r[-2] + r[-1]

      if epigeneticMark == None:
        epigeneticMark = em
      elif epigeneticMark != None and epigeneticMark != em:
        print "datatype was set %s but new is %s" %(epigeneticMark, em) 

      meta["epigenetic_mark"] = epigeneticMark

      # TODO: get sample_id here and remove bio_sample from the attribute_mapper

      ds = Dataset(file_name, meta["type"], meta)
      self.datasets.add(ds)
      if ds.exists():
        continue

      new +=1
    

    log.info("found %d new datasets in %s", new, self)
