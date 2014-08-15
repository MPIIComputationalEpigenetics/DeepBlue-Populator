import threading
import os.path
import traceback

import util
from dataset import Dataset
from settings import max_threads, max_downloads
from log import log
from db import mdb

"""
NonpersistantRepository exception is raised if certain operations on a
repository are attempted before it has been saved to the database.
"""
class NonpersistantRepository(Exception):
  def __init__(self, repo, msg):
    super(NonpersistantRepository, self).__init__()
    self.repository = repo
    self.msg = msg

  def __str__(self):
    return "%s has not been stored: %s" % os.path.join(self.repository, self.msg)

"""
A Repository refers to a source of datasets belonging to a certain project.
It detects the available datasets in the repository and can coordinate their
retrival and processing.
"""
class Repository(object):

  def __init__(self, proj, genome, data_types, path, user_key):
    self._id = None

    self.project = proj
    self.genome = genome
    self.data_types = data_types
    self.path = path
    self.user_key = user_key

    self.datasets = set([])

  def __str__(self):
    return "<Repository: [%s, %s]>" % (self.project, self.path)

  def __eq__(self, other):
    if not isinstance(other, Repository):
      return False
    return self.path == other.path

  def __hash__(self):
    return hash(self.path)


  """
  index_path is the path to the file which contains information of all
  datasets in the repository.
  """
  @property
  def index_path(self):
    pass

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
    pass


  """
  exists checks if the repository has already been added to the database.
  """
  def exists(self):
    return mdb.repositories.find({
        "project": self.project, "path": self.path}).count() > 0

  """
  has_unimported checks if the repository
  """
  def has_unimported(self):
    return mdb.datasets.find({
      "$and": [
      {"repository_id": self.id },
      {"type": { "$in" : self.data_types }},
      {"$or": [
        {"imported": False },
        {"imported": {"$exists": False }} ]}
    ]}).count() > 0


  # save saves the repository to the database if it doesn't exist already.
  def save(self):
    if self.exists():
      return

    doc = {
        "project": self.project,
        "genome": self.genome,
        "path": self.path
      }
    if self.id:
      doc["_id"] = self.id

    log.debug("saving repository: %s", doc)
    r_id = mdb.repositories.save(doc)


  """
  save_datasets saves all the datasets that have been read before.
  Note: it's required to call read_datasets before this method can do anything.
  """
  def save_datasets(self):
    if not self.id:
      raise NonpersistantRepository(self, "cannot save datasets for unsaved repository")

    for ds in self.datasets:
      ds.repository_id = self.id
      ds.save()


  """
  process_datasets starts downloading and processing of all datasets in the
  database that belong to the repository and have not been imported yet.
  """
  def process_datasets(self, key=None):
    if not self.id:
      raise NonpersistantRepository(self, "cannot process datasets for unsaved repository")

    # get all datasets that aren't imported and have the desired type
    rep_files = list(mdb.datasets.find({
      "$and": [
        {"repository_id": self.id },
        {"type": { "$in" : self.data_types }},
        {"$or": [
          {"imported": False },
          {"imported": {"$exists": False }} ]}
      ]}
    ))

    log.info("%d datasets in %s require processing", len(rep_files), self)

    threads = []
    load_sem = threading.Semaphore(max_downloads)
    process_sem = threading.Semaphore(max_threads)

    def process(dataset):
      try:
        dataset.load(load_sem)
        dataset.process(key, process_sem)
        # once we get here everything went successful
        dataset.imported = True
        dataset.save()
      except IOError as ex:
        log.exception("error on downloading or reading dataset of %s failed: %s", dataset, ex)
      except Exception as ex:
        log.exception("processing of %s failed %s", dataset, repr(ex))

    for e in rep_files:
      # reconstruct Datasets from database
      ds = Dataset(e["file_name"], e["type"], e["meta"], e["file_directory"], e["sample_id"], e["repository_id"], e["imported"])
      ds.id = e["_id"]
      # create download dirs
      p = os.path.split(ds.download_path)[0]
      if not os.path.exists(p):
        os.makedirs(p)
      # start processing
      t = threading.Thread(target=process, args=(ds,))
      t.start()
      threads.append(t)
      break

    for t in threads:
      t.join()
