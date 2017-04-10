import requests

from repository import Repository

GET_RELEASE_URL = "http://epigenomesportal.ca/cgi-bin/api/getReleases.py"
GET_DATA_URL = "http://epigenomesportal.ca/cgi-bin/api/getDataHub.py"



class IhecDataPortal:

  @staticmethod
  def get_releases():
    response = requests.get(GET_RELEASE_URL)
    releases = response.json()

    kvs = {}

    for release in releases:
      kvs[(release["publishing_group"], release["assembly"])] = release

    return kvs

  @staticmethod
  def get_release(publishing_group, assembly):
    releases = IhecDataPortal.get_releases()

    kv = releases.get((publishing_group, assembly))

    return kv

  @staticmethod
  def get_release_id(publishing_group, assembly):
    kv = IhecDataPortal.get_release(publishing_group, assembly)
    print kv
    if not kv:
      return None

    return kv["id"]

  @staticmethod
  def get_release_data(publishing_group, assembly):
    release_id = IhecDataPortal.get_release_id(publishing_group, assembly)

    print release_id

    payload = {}
    payload["data_release_id"] = release_id
    response = requests.get(GET_DATA_URL, params=payload)
    release_data = response.json()
    print release_data

class IhecDataRepository(Repository):
  def __init__(self, proj, genome, path):
    super(IhecDataRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed", "bigBed", "bigWig"], path)

  def __str__(self):
    return "<IHEC Data Repository: [%s, %s, %s]>" % (self.proj, self.path, self.data_types)


  def read_datasets(self):
    pass

if __name__ == "__main__":
  IhecDataPortal.get_release_data("CREST", "hg38")
