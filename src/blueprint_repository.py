import os.path
import urllib
import util
import traceback
import threading
import os.path

from dataset import Dataset
from repository import Repository
from settings import DOWNLOAD_PATH, DEEPBLUE_HOST, DEEPBLUE_PORT, max_threads
from log import log
from db import mdb

import pprint
import util

from client import EpidbClient

pp = pprint.PrettyPrinter(depth=6)

class BlueprintRepository(Repository):

  def __init__(self, proj, genome, path, user_key):
    super(BlueprintRepository, self).__init__(proj, genome, ["bed", "wig"], path, user_key)

  def __str__(self):
    return "<Blueprint Repository: [%s, %s]>" % (self.path, self.data_types)

  """
  index_path is the path to the file which contains information of all
  datasets in the repository.
  """
  @property
  def index_path(self):
    return self.path + "blueprint/releases/current_release/homo_sapiens/20140811.data.index"

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

    bio_source_info_keys = ["BIOMATERIAL_TYPE", "CELL_TYPE", "DISEASE", "TISSUE_TYPE"]

    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    for s in sample_extra_info_keys:
      (s, sf_id) = epidb.add_sample_field(s, "string", None, self.user_key)
      if util.has_error(s, sf_id, []): print sf_id

    new = 0
    print self.index_path
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

      if line_info["BIOMATERIAL_TYPE"].lower() == "primary cell":
        bio_source_name = line_info["CELL_TYPE"]
      elif line_info["BIOMATERIAL_TYPE"].lower() == "cell line":
        bio_source_name = line_info["DISEASE"]
      elif line_info['BIOMATERIAL_TYPE'].lower() == "primary cell culture":
        bio_source_extra_info = line_info['SAMPLE_SOURCE']
      else:
        print 'Invalid BIOMATERIAL_TYPE: ', line_info['BIOMATERIAL_TYPE']

      if bio_source_name.lower() == "none":
        print "Invalid bio source name:", bio_source_name
        pp.pprint(line_info)
        continue

      bio_source_extra_info = {}
      for k in bio_source_info_keys:
        i = line_info[k]
        if i != "NA" and  i !="None" and i != "-":
          bio_source_extra_info[k] = i

      bio_source_extra_info["source"] = "BLUEPRINT"

      if bio_source_name not in exists_bio_sources:
        (s, bs_id) = epidb.add_bio_source(bio_source_name, None, bio_source_extra_info, self.user_key)
        if s == "okay":
          print "New Bio Source inserted :", bio_source_name
        else:
          exists_bio_sources.append(bio_source_name)
          if util.has_error(s, bs_id, ["104001"]): print s, bs_id

      if bio_source_extra_info.has_key("TISSUE_TYPE") and bio_source_extra_info["TISSUE_TYPE"] not in exists_bio_sources:
        (s, bs_id) = epidb.add_bio_source(bio_source_extra_info["TISSUE_TYPE"], None, {"source": "Blueprint Epigenomics"}, self.user_key)
        if s == "okay":
          print 'New bio source (tissue) inserted:', bio_source_extra_info['TISSUE_TYPE']
        else:
          exists_bio_sources.append(bio_source_extra_info["TISSUE_TYPE"])
          if util.has_error(s, bs_id, ["104001"]): print s, bs_id

        (s, r) = epidb.set_bio_source_scope(bio_source_extra_info["TISSUE_TYPE"], bio_source_name, self.user_key)
        if util.has_error(s, r, ["104901"]): print s, r

      (s, samples) = epidb.list_samples(bio_source_name, sample_extra_info, self.user_key)
      if samples:
        sample_id = samples[0][0]
      else:
        (s, sample_id) = epidb.add_sample(bio_source_name, sample_extra_info, self.user_key)
        if util.has_error(s, sample_id, []):
          print "BLUEPRIN ERROR PLACE"
          print bio_source_name
          print sample_extra_info
          return

      file_path = line_info["FILE"]
      file_full_name = file_path.split("/")[-1]

      file_type = file_full_name.split(".")[-1]
      if file_type == "gz":
        file_type = file_full_name.split(".")[-2]
      elif file_type == "bw":
        file_type = "bigwig"
      directory = os.path.dirname(file_path)

      meta = line_info

      ds = Dataset(file_path, file_type, meta, file_directory=directory, sample_id=sample_id)
      self.datasets.add(ds)
      if ds.exists():
        continue

      new += 1
      self.has_updates = True

