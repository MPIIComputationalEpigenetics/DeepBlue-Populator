import os
import urllib

import settings

from client import EpidbClient
from settings import DEEPBLUE_HOST, DEEPBLUE_PORT, log

"""
A Vocabulary has a source which is a file or an URL. It can read cell line
and antibody entries from the source.
"""
class ControledVocabulary:

  def __init__(self, fromURL=False):
    self.bio_sources = []
    self.antibodies = []

    f = self._load_data(fromURL)
    self.data = self._process_data(f)
    f.close()

  """
  parses the data in the provided file and fills the antibody and cell line lists.
  """
  def _process_data(self, f):
    current = None

    for line in f:
      line = line.strip()
      if len(line) == 0 or line[0] == "#":
        continue

      (key, value) = line.split(" ", 1)

      if key == "term":
        # new "term" key finishes the last object
        if current:
          if current["type"] == "Cell Line":
            self.bio_sources.append(current)
          elif current["type"] == "Antibody" and not "_(" in current["term"]:
            self.antibodies.append(current)

        # start a new object
        current = {}
        current["term"] = value

      # normalize key
      if key == "targetDescription":
        key = "description"

      # add key-value pair if desired
      #if key in ["deprecated", "type", "organism", "target", "description", "term", "tag", "tissue", "targetClass", "tissue", 
      # "lineage", "karyotype", "sex"]:
      current[key] = value.strip()

    # add very last object
    if current:
      if current["type"] == "Cell Line":
        self.bio_sources.append(current)
      elif current["type"] == "Antibody" and not "_(" in current["term"]:
          self.antibodies.append(current)


  """
  retrieves the file from the filesystem or URL and returns it
  """
  def _load_data(self, fromURL):
    if fromURL:
      f = urllib.urlopen(settings.VOCAB_URL)
    else:
      f = file(os.path.join(settings.DATA_DIR, "cv/cv.ra"))
    return f

def process_bio_source(i, children_map, user_key):
  epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

  bio_source_name = i["term"]

  print "Inserting bio_source " + bio_source_name
  print "ENCODE : epidb.add_bio_source(" + bio_source_name+ ",None,{},"+user_key+")"
  res = epidb.add_bio_source(bio_source_name, None, {}, user_key)
  print res

  if i.has_key("childOf"):
    children_map[bio_source_name] = i["childOf"]

  else:
    if (i.has_key("tissue")):
      res = epidb.add_bio_source(i["tissue"], None, {}, user_key)
      print res
      res = epidb.set_bio_source_scope(i["tissue"], bio_source_name, user_key)
      print res

    if (i.has_key("lineage")):
      lineages = i["lineage"].split(",")
      for lineage in lineages:
        if lineage == "missing":
          continue
        res = epidb.add_bio_source(lineage, None, {}, user_key)
        print res

        if (i.has_key("tissue")):
          res = epidb.set_bio_source_scope(lineage, i["tissue"], user_key)
          print res
        else:
          res = epidb.set_bio_source_scope(lineage, bio_source_name, user_key)
          print res

  fields = {}

  if (i.has_key("karyotype")):
    fields["karyotype"] = i["karyotype"]

  if (i.has_key("lab")):
    fields["lab"] = i["lab"]

  if (i.has_key("lineage")):
    fields["lineage"] = i["lineage"]

  if (i.has_key("organism")):
    fields["organism"] = i["organism"]

  if (i.has_key("sex") and i["sex"] != "U"):
    fields["sex"] = i["sex"]

  if (i.has_key("tier")):
    fields["tier"] = i["tier"]

  if (i.has_key("age") and i["age"] != "ageUnknown"):
    fields["age"] = i["age"]

  if (i.has_key("strain") and i["strain"] != "Unknown"):
    fields["strain"] = i["strain"]

  if (i.has_key("description")):
    fields["description"] = i["description"]

  res = epidb.add_sample(bio_source_name, fields, user_key)

"""
ensure_vocabulary retrieves a set of cell line and antibody vocabulary and
adds them to Epidb.
Note: This method should be called initially. Datasets with unknown vocabulary
will be rejected by Epidb.
"""
def ensure_vocabulary(user_key):
  epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

  voc = ControledVocabulary()
  log.info("adding %d bio_source to the vocabulary", len(voc.bio_sources))
  log.info("adding %d antibodies to the vocabulary", len(voc.antibodies))

  # add bio_sources to epidb
  children_map = {}
  for cl in voc.bio_sources:
    process_bio_source(cl, children_map, user_key) 

  for (bio_source_name, parent) in children_map.iteritems():
    res = epidb.set_bio_source_scope(parent, bio_source_name, user_key)

  # add antibodies to epidb
  for ab in voc.antibodies:
    res = epidb.add_epigenetic_mark(ab["term"],  ab["description"], user_key=user_key)
    log.debug("adding bio_source %s; result: %s", (ab["target"], ab["description"]), res)

  log.info("vocabulary added successfully")    
