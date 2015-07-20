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
        self.process_encode_experiment(experiment["@id"])

        """
        for file in graph.get("files", []):
          total =+ 1

          if file['file_type'] in ["fastq", "bam"]: continue

          pprint.pprint(file)

          replicate = file.get("replicate", {})
          if not replicate: continue

          library = replica.get("library", {})
          if not library: continue

          biosample = library.get("biosample", {})
          if not biosample: continue

          sample = replicate["library"]["biosample"]
          biosource_term_id = sample["biosample_term_id"]
          (status, (bs,)) = epidb.list_biosources({"ontology_id":biosource_term_id})
          (s, sid) = epidb.add_sample(bs[1], sample)
          #print sample
          print s, sid

          experiment = replicate.get("experiment", {})
          files = replicate.get("files", {})

          ds = Dataset(file["href"], file["file_format"], file, sample_id=sid)
          if self.add_dataset(ds):
            new += 1
            self.has_updates = True
        log.info("found %d new datasets in %s", new, self)
        """

  def process_encode_experiment(self, _id) :
    url = self.path + _id
    response = requests.get(url, params={'format':'json'})
    print response.url
    print response
    response_json_dict = response.json()
    print response_json_dict

