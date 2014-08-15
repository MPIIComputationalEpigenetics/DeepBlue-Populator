import os
import gzip
import util

from subprocess import call

from attribute_mapper import do_map
from formats import format_builder
from settings import DOWNLOAD_PATH, DEEPBLUE_HOST, DEEPBLUE_PORT, OS
from log import log
from db import mdb

from bedgraphtowig import try_to_convert

from client import EpidbClient

"""
MissingFile exception is raised if the file at the given path cannot be found.
"""
class MissingFile(Exception):
  def __init__(self, p, f):
    super(MissingFile, self).__init__()
    self.path = p
    self.file = f

  def __str__(self):
    return "MissingFile: %s" % os.path.join(self.path, self.file)

"""
OrphanedDataset exception is raised if the given dataset cannot be assigned to
a specific repository, which should also be persistent in the database.
"""
class OrphanedDataset(Exception):
  def __init__(self, ds, msg):
    super(OrphanedDataset, self).__init__()
    self.dataset = ds
    self.msg = msg

  def __str__(self):
    return "%s has no parent repository defined: %s" % (self.dataset, self.msg)


"""
Dataset is a logical unit describing a set of data that can be found at
a certain destination. It holds meta data coresponding to the data and is
used to process and insert data into epidb.
"""
class Dataset:

  def __init__(self, file_name, type_, meta={}, file_directory=None, sample_id=None, repo_id=None, imported=False):

    self.file_name = file_name
    self.type_ = type_
    self.meta = meta
    self.file_directory = file_directory
    self.sample_id = sample_id
    self.repository_id = repo_id
    self.imported = imported
    self._id = None

    # plain map as received from database (not a Repository object)
    self._repository = None

  def __str__(self):
    return "<Dataset at %s>" % (self.download_path)

  def __eq__(self, other):
    if not isinstance(other, Dataset):
      return False
    return self.repository_id == other.repository_id and self.file_name == other.file_name

  def __hash__(self):
    return (hash(self.repository_id) << 16) ^ hash(self.file_name)

  @property
  def id(self):
    if self._id:
      return self._id

    # load id if dataset exists but id is unknown
    if self.exists():
      doc = mdb.datasets.find_one({
        "repository_id": self.repository_id,
        "file_name": self.file_name
      })
      if doc and doc["_id"]:
        self._id = doc["_id"]
        return self._id
    return None

  @id.setter
  def id(self, val):
    self._id = val


  @property
  def repository(self):
    if not self.repository_id:
      raise OrphanedDataset("cannot get repository without id")
    # only keep cache as long as it matches the repository_id
    if self._repository and self._repository["_id"] == self.repository_id:
      return self._repository
    self._repository = mdb.repositories.find_one({"_id": self.repository_id})
    return self._repository


  """
  exists checks if the Dataset with its unique attributes `repository_id' and
  'file_name' exists in the database.
  """
  def exists(self):
    return mdb.datasets.find({
        "repository_id": self.repository_id,
        "file_name": self.file_name
      }).count() > 0


  """
  save saves the dataset with its meta information to the database
  Note: this does not have anything to do with the actual genetic data
  that belongs to this dataset.
  """
  def save(self):
    if not self.repository_id:
      raise OrphanedDataset("datasets cannot be saved without a repository id")

    doc = {
        "file_name": self.file_name,
        "repository_id": self.repository_id,
        "type":self.type_,
        "imported": self.imported,
        "meta": self.meta,
        "file_directory":self.file_directory,
        "sample_id": self.sample_id
      }
    # update existing dataset if id is known/it exists
    if self.id:
      doc["_id"] = self.id

    ds_id = mdb.datasets.save(doc)


  """
  download_path is the path where the datasetes data file is stored
  """
  @property
  def download_path(self):
    if not self.repository_id:
      raise OrphanedDataset(self, "download path cannot be determined without repository.")

    return os.path.join(DOWNLOAD_PATH, str(self.repository_id), self.file_name.replace("ftp://","").replace("http://",""))

  """
  load downloads the actual data this dataset refers to if it hasn't
  been loaded already.
  """
  def load(self, sem=None):
    if sem:
      with sem:
        self._load()
    else:
      self._load()

  def _load(self):
    if os.path.exists(self.download_path):
      log.info("%s already downloaded", self)
      return

    if not self.repository_id:
      raise OrphanedDataset(self, "cannot load dataset for unknown repository.")

    rep = mdb.repositories.find_one({"_id": self.repository_id})
    if not rep:
      raise OrphanedDataset(self, "coresponding repository doesn't exist.")

    if self.file_name.startswith("http://") or self.file_name.startswith("ftp://"):
      url = self.file_name
    else:
      url = os.path.join(rep["path"], self.file_name)

    util.download_file(url, self.download_path)
    log.info("Download finished %s", url)

  """
  process inserts the downloaded file and specific meta data into Epidb.
  Note: the file must have been downloaded before (c.f. load) method.
  """
  def process(self, user_key=None, sem=None):
    if sem:
      with sem:
        self._process(user_key)
    else:
      self._process(user_key)

  def _process(self, user_key=None):
    log.info("processing dataset %s", self)

    project = self.repository["project"]
    if self.meta.has_key("epigenetic_mark"):
      mark = self.meta["epigenetic_mark"]
      am = do_map(project, mark)(self)
    else:
      am = do_map(project)(self)

    if not os.path.exists(self.download_path):
      raise MissingFile(self.download_path, self.file_name)

    # Handle crazy ENCODE big wigs, that can be bedgraph, bedgraph that can be converted to wig, and... wig!
    if self.meta.has_key("type") and self.meta["type"] == "bigWig":
      print "../third_party/bigWigToWig."+OS + " " + self.download_path + " " +  self.download_path+".wig"
      call(["../third_party/bigWigToWig."+OS, self.download_path, self.download_path+".wig"])

      wig_file = self.download_path+".wig"

      f = open(wig_file, 'r')
      wig_content = f.read()

      wig_content = wig_content.split("\n", 1)
      first_line = wig_content[0]
      while first_line[:1] == "#" or first_line[:5] == "track" or first_line[:7] == "browser":
        wig_content = wig_content[1]
        wig_content = wig_content.split("\n", 1)
        first_line = wig_content[0]
        log.debug(first_line)

      wig_content = "\n".join(wig_content)
      first_word = first_line.split()[0]
      if first_word == "variableStep" or first_word == "fixedStep":
          frmt = "wig"
          file_content = wig_content
      else:
        (status, content) = try_to_convert(wig_file)

        if status:
          frmt = "wig"
          file_content = content
        else:
          frmt = "bedgraph"
          f = open(wig_file, 'r')
          file_content = wig_content
          f.close()

      os.unlink(self.download_path+".wig")

    elif self.type_ == "wig":
      if self.download_path.endswith("gz"):
        f = gzip.open(self.download_path, 'rb')
      else:
        f = open(self.download_path, 'rb')

      file_content = f.read()
      frmt = "wig"

    else:
      file_type = self.download_path.split(".")[-1]
      if file_type == "gz":
        f = gzip.open(self.download_path, 'rb') # gzip doc says `with' is supported - seems its not
      else:
        f = open(self.download_path, 'r')

      file_content = f.read()
      f.close()

      file_split = file_content.split("\n", 1)
      first_line = file_split[0]

      while (first_line[:1] == "#" or first_line[:5] == "track" or first_line[:7] == "browser"):
        file_content = file_split[1]
        file_split = file_content.split("\n", 1)
        first_line = file_split[0]
        log.debug(first_line)

      extra_info_size = len(first_line.split())

      frmt = format_builder(am.format, extra_info_size)

      data_splited = file_content.split("\n")
      data_splited = [x for x in data_splited if x]
      data_splited.sort()
      file_content = "\n".join(data_splited)


    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    if self.sample_id:
      sample_id = self.sample_id
    else:
      (status, samples_id) = epidb.list_samples(am.bio_source, {}, user_key)
      if status != "okay" or not len(samples_id):
        log.critical("Sample for biosource %s was not found", am.bio_source)
        log.critical(samples_id)
        return
      sample_id = samples_id[0][0]

    args = (am.name, am.genome, am.epigenetic_mark, sample_id, am.technique,
            am.project, am.description, file_content, frmt, self.meta, user_key)

    res = epidb.add_experiment(*args)
    if res[0] == "okay":
      log.info("dataset %s inserted ", am.name)
    else:
      log.info("Error while inserting dataset: %s\n%s\n%s\n%s", res, am.name, frmt, file_content[0:500])
