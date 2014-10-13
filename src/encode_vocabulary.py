import os
import urllib

import settings
import util

from client import EpidbClient
from settings import DEEPBLUE_HOST, DEEPBLUE_PORT
from log import log

"""
A Vocabulary has a source which is a file or an URL. It can read cell line
and antibody entries from the source.
"""
class ControledVocabulary:

  def __init__(self, fromURL=False):
    self.biosources = []
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
            self.biosources.append(current)
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
        self.biosources.append(current)
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

def process_biosource(i, children_map, user_key):
  epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

  biosource_name = i["term"]

  (s, r) = epidb.add_biosource(biosource_name, None, {"source": "ENCODE"}, user_key)
  if util.has_error(s, r, ["104001"]):
    print "(ENCODE CV Error 1): ", r

  if i.has_key("childOf"):
    children_map[biosource_name] = i["childOf"]

  else:
    if (i.has_key("tissue")):
      (s, r) = epidb.add_biosource(i["tissue"], None, {"source": "ENCODE"}, user_key)
      if util.has_error(s, r, ["104001"]): print "(ENCODE CV Error 2): ", r

      if (i["tissue"].lower().replace(" ", "") != biosource_name.lower().replace(" ", "")):
        (s, r) = epidb.set_biosource_scope(i["tissue"], biosource_name, user_key)
        if util.has_error(s, r, ["104901"]): print "(ENCODE CV Error 3): ", r

    if (i.has_key("lineage")):
      lineages = i["lineage"].split(",")
      for lineage in lineages:
        if lineage == "missing":
          continue
        (s, r) = epidb.add_biosource(lineage, None, {"source": "ENCODE"}, user_key)
        if util.has_error(s, r, ["104001"]): print "(ENCODE CV Error 4): ", r

        if (i.has_key("tissue")):
          (s, r) = epidb.set_biosource_scope(lineage, i["tissue"], user_key)
          if util.has_error(s, r, ["104901"]): print "(ENCODE CV Error 5): ", r
        else:
          (s, r) = epidb.set_biosource_scope(lineage, biosource_name, user_key)
          if util.has_error(s, r, ["104901"]): print "(ENCODE CV Error 6): ", r

  fields = {}

  if (i.has_key("karyotype")):
    fields["karyotype"] = i["karyotype"]

  if (i.has_key("lineage")):
    fields["lineage"] = i["lineage"]

  if (i.has_key("lab")):
    fields["lab"] = i["lab"]

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

  fields["source"] = "ENCODE"
  (s, s_id) = epidb.add_sample(biosource_name, fields, user_key)
  if util.has_error(s, s_id, []): print "(ENCODE CV Error 7): " ,s_id

"""
ensure_vocabulary retrieves a set of cell line and antibody vocabulary and
adds them to Epidb.
Note: This method should be called initially. Datasets with unknown vocabulary
will be rejected by Epidb.
"""
def ensure_vocabulary(user_key):
  epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

  voc = ControledVocabulary()
  log.info("adding %d biosource to the vocabulary", len(voc.biosources))
  log.info("adding %d antibodies to the vocabulary", len(voc.antibodies))

  # add biosources to epidb
  children_map = {}
  for cl in voc.biosources:
    process_biosource(cl, children_map, user_key)

  for (biosource_name, parent) in children_map.iteritems():
    (s, bs_id) = epidb.set_biosource_scope(parent, biosource_name, user_key)
    if util.has_error(s, bs_id, []): print "(ENCODE CV Error 8): ", bs_id

  # add antibodies to epidb
  for ab in voc.antibodies:
    log.debug("(Encode) Inserting epigenetic_mark %s", ab["target"])
    (s, em_id) = epidb.add_epigenetic_mark(ab["term"],  ab["description"], user_key=user_key)
    if util.has_error(s, em_id, ["105001"]): print "(ENCODE CV Error 8): ", em_id

  log.info("vocabulary added successfully")
