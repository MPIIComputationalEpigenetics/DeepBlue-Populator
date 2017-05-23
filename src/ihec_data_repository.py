import requests
from pprint import pprint

from repository import Repository
from epidb_interaction import PopulatorEpidbClient

from dataset import Dataset

from collections import defaultdict

GET_RELEASE_URL = "http://epigenomesportal.ca/cgi-bin/api/getReleases.py"
GET_DATA_URL = "http://epigenomesportal.ca/cgi-bin/api/getDataHub.py"


class IhecDataPortal:

  @staticmethod
  def get_releases():
    response = requests.get(GET_RELEASE_URL)
    releases = response.json()

    kvs = defaultdict(list)
    for release in releases:
      kvs[(release["publishing_group"], release["assembly"])].append(release)
    return kvs

  @staticmethod
  def get_releases_info(publishing_group, assembly):
    releases = IhecDataPortal.get_releases()
    return releases.get((publishing_group, assembly))

  @staticmethod
  def get_releases_id(publishing_group, assembly):
    releases = IhecDataPortal.get_releases_info(publishing_group, assembly)
    ids = []
    if not releases: 
      return ids
    for release in releases:
      ids.append(release["id"])
    return ids

  @staticmethod
  def get_releases_data(publishing_group, assembly):
    releases_id = IhecDataPortal.get_releases_id(publishing_group, assembly)

    data = []
    for id in releases_id:
      payload = {}
      payload["data_release_id"] = id
      response = requests.get(GET_DATA_URL, params=payload)
      release_data = response.json()
      data.append(release_data)

    return data

class IhecDataRepository(Repository):
  def __init__(self, proj, genome, path):
    super(IhecDataRepository, self).__init__(proj, genome, [ "signal_unstranded", "methylation_profile", "signal_forward", "signal_reverse" ], path)

  def __str__(self):
    return "<IHEC Data Repository: [%s, %s, %s]>" % (self.project, self.path, self.data_types)

  def read_datasets(self):
    epidb = PopulatorEpidbClient()
    ihec_project = self.project
    if ihec_project == "DEEP (IHEC)":
      ihec_project = "DEEP"
    releases = IhecDataPortal.get_releases_data(ihec_project, self.genome)

    for j in releases:
      hub_description = j['hub_description']

      genome = hub_description['assembly']
      releasing_group = hub_description['releasing_group']
      project_description = hub_description['description']
      description_url = hub_description.get('description_url')

      if description_url:
        project_description = project_description + " (" + description_url + ")"


      add_project = (self.project, project_description)

      print epidb.add_project(*add_project)
      datasets = j["datasets"]
      samples = j["samples"]
      map_sample = {}
      for s_id in samples:
          sample = samples[s_id]
          sample["source"] = self.project
          biosource_url = sample['sample_ontology_uri'].split(";")[0]
          ontology_id = biosource_url.split("/")[-1]
          oid_s = ontology_id.split("_")
          ontology_id = oid_s[0] + ":" + oid_s[1]
          s, bs = epidb.list_biosources({"ontology_id": ontology_id})
          biosource = bs[0][1]
          add_sample = (biosource, sample)
          map_sample[s_id] = add_sample

      for d in datasets:
          dataset = datasets[d]
          dataset_name = d
          sample_id = dataset['sample_id']
          epigenetic_mark = dataset['experiment_attributes']['experiment_type']
          technique = dataset['experiment_attributes'].get('assay_type')
          sample = map_sample[dataset['sample_id']]
          (status, db_sample_id) = epidb.add_sample(sample[0], sample[1])
          extra_metadata = {}
          extra_metadata.update(dataset.get('experiment_attributes', {}))
          extra_metadata.update(dataset.get('analysis_attributes', {}))
          extra_metadata.update(dataset.get('ihec_data_portal', {}))
          extra_metadata.update(dataset.get('other_attributes', {}))
          if dataset.get("raw_data_url"):
              extra_metadata["raw_data_url"] = dataset.get("raw_data_url")

          extra_metadata['releasing_group'] = releasing_group
          for f in dataset['browser']:
              file = dataset['browser'][f][0]
              data_url = file['big_data_url']
              extra_metadata['data_type'] = f
              name = data_url.split("/")[-1]
              meta = {"genome": genome,
                          "epigenetic_mark": epigenetic_mark,
                          "sample": db_sample_id,
                          "technique": technique,
                          "project": self.project,
                          "data_url": data_url,
                          "extra_metadata": extra_metadata}

              ds = Dataset(data_url, f, meta, sample_id=db_sample_id)
              if self.add_dataset(ds):
                self.has_updates = True

