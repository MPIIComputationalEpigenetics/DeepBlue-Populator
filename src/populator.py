import os
import os.path
import settings

import encode_vocabulary
import column_definitions
import repository_factory

from annotations import insert_annotations
from client import EpidbClient
from data_sources import project_sources
from genomes import hg19_info, mm9_info
from histones import insert_histones
from owl_loader import load_owl
from settings import DEEPBLUE_HOST, DEEPBLUE_PORT
from log import log
from db import mdb

"""
The Populator maintains the database connection and delegates
tasks to its repositories and their datasets.
"""
class Populator:
  # epidb access data
  username = settings.EPIDB_POPULATOR_USER[0]
  email = settings.EPIDB_POPULATOR_USER[1]
  institution = settings.EPIDB_POPULATOR_USER[2]
  key = None

  def __init__(self):
    self.repositories = set([])

    if os.path.exists(settings.EPIDB_AUTHKEY_FILE):
      self.load_auth_info()

  def __str__(self):
    return "<Populator>"

  """
  setup_epidb sets up access to epidb
  """
  def setup_epidb(self):
    if os.path.exists(settings.EPIDB_AUTHKEY_FILE):
      log.error("setup file %s for epidb already exists", settings.EPIDB_AUTHKEY_FILE)
      # XXX: exit?
      return False

    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)
    res, admin_key = epidb.init_system(*settings.EPIDB_INIT_USER)
    if (res == "error"):
      log.error("error while initializing the system: %s", admin_key)
      return False

    log.info("admin user created successfully")

    res, u = epidb.add_user(self.username, self.email, self.institution, admin_key)
    if (res == "error"):
      log.error("error while adding populator user: %s", u)
      return False

    user_id, key = u

    self.key = key
    log.info("populator user created successfully")

    with open(settings.EPIDB_AUTHKEY_FILE, 'w') as f:
      f.write("%s:%s:%s:%s" % (settings.EPIDB_INIT_USER + (admin_key,)))
      f.write('\n')
      f.write("%s:%s:%s:%s" % (settings.EPIDB_POPULATOR_USER + (key,)))

    return True

  """
  load_auth_info loads a previously obtained authentication key for
  epidb from the key file, defined in the settings.
  """
  def load_auth_info(self):
    with open(settings.EPIDB_AUTHKEY_FILE, 'r') as f:
      for l in f.readlines():
        (user, email, inst, key) = l.split(':')
        if (user, email, inst) == (self.username, self.email, self.institution):
          self.key = key
          break

    log.info("loaded authentication key successfully")


  def insert_basic_data(self):
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    self.insert_genomes()
    self.insert_epigenetic_marks()
    self.insert_technologies()
    self.insert_projects()
    self.insert_sample_fields()

  def insert_genomes(self):
    # TODO: Load these information from the source file.
    # TODO: check the source for the genome, if not, add it.
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    epidb.add_genome("hg19", "Human Genome Assembly hg19", hg19_info, self.key)
    epidb.add_genome("mm9", "Mouse Genome Assembly mm9", mm9_info, self.key)
    #insert_chromosome_sequences(epidb, "hg19", self.key)


  def insert_epigenetic_marks(self):
    # TODO: enforce in the datasource the epigenetic mark
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    epidb.add_epigenetic_mark("Methylation", "DNA Methylation", self.key)
    epidb.add_epigenetic_mark("DNaseI", "DNaseI hypersensitive sites", self.key)
    epidb.add_epigenetic_mark("TFBS", "Transcription factor binding sites", self.key)
    epidb.add_epigenetic_mark("Chromatin State Segmentation",  "A common set of states across the cell types were learned by computationally integrating ChIP-seq data for nine factors plus input using a Hidden Markov Model (HMM). In total, fifteen states were used to segment the genome.", self.key)
    epidb.add_epigenetic_mark("mRNA-seq", "Messenger RNA", self.key)
    epidb.add_epigenetic_mark("Input", "Experiment Input Data. It is not an epigenetic mark", self.key)
    epidb.add_epigenetic_mark("Control", "Experiment Control Data. It is not an epigenetic mark", self.key)

    insert_histones(epidb, self.key)

  def insert_technologies(self):
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    epidb.add_technique("RRBS", "Reduced representation bisulfite sequencing", {}, self.key)
    epidb.add_technique("Infinium 450k", "Infinium HumanMethylation450", {}, self.key)
    epidb.add_technique("BisulfiteSeq", "Bisulfite sequencing or Bisulphite sequencing", {}, self.key)
    epidb.add_technique("ChipSeq", "ChIP-sequencing", {}, self.key)
    epidb.add_technique("ChipSeq Uniform", "ChIP-sequencing performed uniform processing on datasets produced by multiple data production groups in the ENCODE Consortium", {}, self.key)
    epidb.add_technique("DNaseSeq", "DNase I hypersensitive sites sequencing", {}, self.key)
    epidb.add_technique("DNaseSeq Uniform", "DNase I hypersensitive sites sequencing performed uniform processing on datasets produced by multiple data production groups in the ENCODE Consortium", {}, self.key)
    epidb.add_technique("Chromatin State Segmentation by HMM", "ChIP-seq data from the Broad Histone track was used to generate this track. Data for nine factors plus input and nine cell types was binarized separately at a 200 base pair resolution based on a Poisson background model. The chromatin states were learned from this binarized data using a multivariate Hidden Markov Model (HMM) that explicitly models the combinatorial patterns of observed modifications (Ernst and Kellis, 2010). To learn a common set of states across the nine cell types, first the genomes were concatenated across the cell types. For each of the nine cell types, each 200 base pair interval was then assigned to its most likely state under the model. Detailed information about the model parameters and state enrichments can be found in (Ernst et al, accepted).", {}, self.key)
    epidb.add_technique("RNASeq", "RNA sequencing", {}, self.key)

  def insert_projects(self):
    # TODO: Load these information from the source file.
    # TODO: put in the source
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    epidb.add_project("ENCODE", "The ENCODE Project: ENCyclopedia Of DNA Elements", self.key)
    epidb.add_project("Blueprint Epigenetics", "BLUEPRINT - A BLUEPRINT of Haematopoietic Epigenomes", self.key)
    epidb.add_project("Mouse ENCODE", "The ENCODE Project: ENCyclopedia Of DNA Elements - Mouse", self.key)


  def insert_sample_fields(self):
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    epidb.add_sample_field("karyotype", "string", None, self.key)
    epidb.add_sample_field("description", "string", None, self.key)
    epidb.add_sample_field("lab", "string", None, self.key)
    epidb.add_sample_field("lineage", "string", None, self.key)
    epidb.add_sample_field("organism", "string", None, self.key)
    epidb.add_sample_field("sex", "string", None, self.key)
    epidb.add_sample_field("tier", "string", None, self.key)
    epidb.add_sample_field("age", "string", None, self.key)
    epidb.add_sample_field("strain", "string", None, self.key)
    epidb.add_sample_field("source", "string", None, self.key)

  def create_columns(self):
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    for col in column_definitions.SIMPLE:
      epidb.create_column_type_simple(*col + (self.key,))
    for col in column_definitions.CATEGORY:
      epidb.create_column_type_category(*col + (self.key,))

    for col in column_definitions.RANGE:
      epidb.create_column_type_range(*col + (self.key,))


  def process_annotations(self):
    insert_annotations(self.key)

  def process_ontology(self):
    load_owl(self.key)
    encode_vocabulary.manual_curation(self.key)
    encode_vocabulary.ensure_vocabulary(self.key)

  """
  setup_collections configures database internals for the Populator database
  """
  def setup_collections(self):
    mdb.repositories.ensure_index([("path", 1)], unique=True)
    mdb.datasets.ensure_index([("file_name", 1), ("repository_id", 1)], unique=True)

  def  load_repositories(self):
    for sources in project_sources:
      for (proj, genome, url) in sources:
        r = repository_factory.load(proj, genome, url, self.key)
        log.info("%s loaded", str(r))
        self.repositories.add(r)
        r.save()
    log.info("populator initialized with %d repositories", len(self.repositories))

  """
  check_reposoitories reads all repositories and flags new datasets.
  """
  def check_repositories(self):
    self.setup_collections()

    for rep in self.repositories:
      rep.read_datasets()

    log.info("repositories checked successfully")


  """
  process_repositories downloads all new datasets and inserts them
  into epidb (processing).
  Note: For this method to take any effect check_repositories must be
  invoked beforehand.
  """
  def process_repositories(self):
    log.info("processing repositories")
    for rep in self.repositories:
      rep.process_datasets(self.key)

    log.info("repositories processed successfully")

