import os.path
import urllib
import util
import traceback
import threading
import os.path

from dataset import Dataset
from settings import mdb, log, max_threads
from repository import Repository

from settings import DOWNLOAD_PATH, DEEPBLUE_HOST, DEEPBLUE_PORT

from client import EpidbClient

class BlueprintRepository(Repository):

  def __init__(self, proj, genome, path, user_key):
    super(BlueprintRepository, self).__init__(proj, genome, ["bed"], path, user_key)

  def __str__(self):
    return "<Blueprint Repository: [%s, %s]>" % (self.path, self.data_types)

  """
  index_path is the path to the file which contains information of all
  datasets in the repository.
  """
  @property
  def index_path(self):
    return self.path + "blueprint/releases/current_release/homo_sapiens/20140317.data.index"

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
    # TODO: convert to the predefined keys
    sample_extra_info_keys = ["SAMPLE_ID", "SAMPLE_NAME", "DISEASE", "BIOMATERIAL_PROVIDER",
        "BIOMATERIAL_TYPE", "DONOR_ID", "DONOR_SEX", "DONOR_AGE", "DONOR_HEALTH_STATUS", "DONOR_ETHNICITY", "DONOR_REGION_OF_RESIDENCE",
        "SPECIMEN_PROCESSING", "SPECIMEN_STORAGE"]

    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    for s in sample_extra_info_keys: 
      epidb.add_sample_field(s, "string", None, self.user_key)

    #remove_fields = ["FILE_MD5", "FILE_SIZE"]
    new = 0
    req = urllib.urlopen(self.index_path)
    content = req.read()
    ucontent = unicode(content, 'iso_8859_1')
    lines = ucontent.split("\n")

    header_keys = lines[0].split()

    for l in lines[1:]:
      if not l.strip():
        continue

      line_info = {}
      values = l.split("\t")

      for i in range(len(header_keys)):
        line_info[header_keys[i]] = values[i]

      sample_extra_info = {}
      for k in sample_extra_info_keys:
        sample_extra_info[k] = line_info[k]
      
      (s, samples) = epidb.list_samples(line_info["CELL_TYPE"], sample_extra_info, self.user_key)
      if samples:
        print "(Blueprint) Reusing sample ", sample_id, " for " , line_info["CELL_TYPE"], " and ", repr(sample_extra_info) 
        sample_id = samples[0]
      else:
        print "(Blueprint) Inserting sample " , line_info["CELL_TYPE"], " and ", repr(sample_extra_info)
        (s, sample_id) = epidb.add_sample(line_info["CELL_TYPE"], sample_extra_info, self.user_key)
        if s == "error":
          r = epidb.add_bio_source(line_info["CELL_TYPE"], None, {}, self.user_key)
          if (r[0] == "error"):
            print r
          else:
            print "(Blueprint) inserted bio source " , line_info["CELL_TYPE"] 
            (s, sample_id) = epidb.add_sample(line_info["CELL_TYPE"], sample_extra_info, self.user_key)
            print "(Blueprint)" , sample_id

      file_path = line_info["FILE"]
      file_full_name = file_path.split("/")[-1]

      file_type = file_full_name.split(".")[-1]
      if file_type == "gz":
        file_type = file_full_name.split(".")[-2]
        
      directory = os.path.dirname(file_path)

      meta = line_info

      # Lets keep all the metadata
      #for field in meta.keys():
      #  if field in remove_fields:
      #    meta.pop(field)

      ds = Dataset(file_path, file_type, meta, file_directory=directory, sample_id=sample_id)
      self.datasets.add(ds)
      if ds.exists():
        continue

      new += 1
      self.has_updates = True
    
