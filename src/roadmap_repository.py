import util
import os
import os.path
import pprint

import gzip

"""
import urllib
import traceback
import threading
import os.path

from dataset import Dataset
from repository import Repository
from settings import DOWNLOAD_PATH, DEEPBLUE_HOST, DEEPBLUE_PORT, max_threads
from log import log
from db import mdb

import util

from client import EpidbClient

class RoadmapRepository(Repository):

  def __init__(self, proj, genome, path, user_key):
    super(RoadmapRepository, self).__init__(proj, genome, ["bed"], path, user_key)

  def __str__(self):
    return "<Roadmap Repository: [%s, %s]>" % (self.path, self.data_types)

  @property
  def index_path(self):
    return self.path

  @property
  def id(self):
    idl = mdb.repositories.find_one({
      "project": self.project, "path": self.path}, ["_id"])
    if not idl:
      return None
    return idl["_id"]

  def read_datasets(self):

    ds = Dataset(file_path, file_type, meta, file_directory=directory, sample_id=sample_id)
    self.datasets.add(ds)
    new += 1
    self.has_updates = True
"""

def clean(s):
  pass

def set_up_bio_sources(server):
  print server.set_bio_source_synonym('Stomach', "Gastric", user_key)
  print server.add_bio_source('Induced pluripotent stem cell line derived from foreskin fibroblasts', 'Induced pluripotent stem cell. Described by Yu, J. et al. Human induced pluripotent stem cells free of vector and transgene sequences. Science 324, 797-801 (2009).', {"source": "Roadmap Epigenomics"}, user_key)

  print server.set_bio_source_scope('Induced pluripotent stem cell', 'Induced pluripotent stem cell line derived from foreskin fibroblasts', user_key)

  print server.add_bio_source('iPS DF 19.11 Cell Line', None, {"source": "Roadmap Epigenomics"}, user_key)
  print server.set_bio_source_synonym('iPS DF 19.11 Cell Line', 'iPS 19.11', user_key)
  print server.set_bio_source_synonym('iPS DF 19.11 Cell Line', 'iPS DF 19.11', user_key)

  print server.add_bio_source('iPS DF 6.9 Cell Line', None, {"source": "Roadmap Epigenomics"}, user_key)
  print server.set_bio_source_synonym('iPS DF 6.9 Cell Line', 'iPS 6.9', user_key)
  print server.set_bio_source_synonym('iPS DF 6.9 Cell Line', 'iPS DF 6.9', user_key)


def set_up_samples_fields(server):
  print server.add_sample_field('batch', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('biomaterial_provider', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('biomaterial_type', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('bisulfite_conversion_percent', 'integer', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('bisulfite_conversion_protocol', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_first_strand_purification', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_first_strand_synthesis_enzyme', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_fragment_size_range', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_fragmentation', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_initial_rna_qnty', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_polya_rna', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_purification', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_second_strand_synthesis_dntp_mix', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('cdna_preparation_second_strand_synthesis_enzyme', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_antibody', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_antibody_catalog', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_antibody_lot', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_antibody_provider', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_protocol', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_protocol_antibody_amount', 'integer', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_protocol_bead_amount', 'integer', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_protocol_bead_type', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('chip_protocol_chromatin_amount', 'integer', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('collection_method', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('differentiation_method', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('differentiation_stage', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('disease', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('dna_preparation_adaptor', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('dna_preparation_adaptor_ligation_protocol', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('dna_preparation_adaptor_sequence', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('dna_preparation_fragment_size_range', 'integer', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('dna_preparation_initial_dna_qnty', 'integer', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('dna_preparation_post-ligation_fragment_size_selection', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('dna_preparation_uracil_dna_glycosylase_digestion', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('donor_age', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('donor_ethnicity', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('donor_health_status', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('donor_id','string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('donor_sex','string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('experiment_type', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('extraction_protocol', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('extraction_protocol_fragmentation', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('extraction_protocol_mrna_enrichment', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('extraction_protocol_sonication_cycles', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('extraction_protocol_type_of_sonicator', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_f_primer_sequence', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_number_cycles', 'integer', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_polymerase_type', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_primer', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_primer_conc', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_product_isolation_protocol', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_r_primer_sequence', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_template', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_template_conc', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('library_generation_pcr_thermocycling_program', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('line', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('medium', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('molecule', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('mrna_preparation_fragment_size_range', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('mrna_preparation_initial_mrna_qnty', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('passage', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('rna_preparation_3\'_rna adapter_ligation_protocol', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('rna_preparation_3\'_rna_adapter_sequence', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('rna_preparation_5\'_dephosphorylation', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('rna_preparation_5\'_phosphorylation', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('rna_preparation_5\'_rna_adapter_ligation_protocol', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('rna_preparation_5\'_rna_adapter_sequence', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('rna_preparation_reverse_transcription_primer_sequence', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('rna_preparation_reverse_transcription_protocol', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('sample alias', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('sample common name', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('sra sample accession','string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('tissue_depot', 'string', "Roadmap Epigenomics Sample Metadata", user_key)
  print server.add_sample_field('tissue_type', 'string', "Roadmap Epigenomics Sample Metadata", user_key)

def process_metadata(_file):
  print _file

  file_metadata = {}
  samples = {}
  f = gzip.open(_file, 'rb')
  for line in f.readlines():
    s_line = line.split("\t")

    if len(s_line) == 2 and len(s_line[1].strip()) > 0 and s_line[0] != "!Series_sample_id":
      k = s_line[0][1:]
      if not file_metadata.has_key(k):
        file_metadata[k] = []
      file_metadata[k].append(s_line[1].strip()[1:-1])

    elif len(s_line) > 2:
      k = s_line[0][1:].strip()

      if k == 'ID_REF"': #removing the " from ID_REF
        k = "ID_REF"

      for pos in range(1, len(s_line[1:]) + 1):
        if not samples.has_key(pos):
          samples[pos] = {}

        content = s_line[pos].strip()[1:-1]
        if len(content.strip()) > 0:
          if not samples[pos].has_key(k):
            samples[pos][k] = []
          samples[pos][k].append(content)

  # Pos processing
  prev_term = ""

  for pos in samples:
    sample = samples[pos]

    for field_name in sample:
      if len(sample[field_name]) == 1:
        sample[field_name] = sample[field_name][0]

      else:
        # Data processing
        if field_name == 'Sample_data_processing':
          Sample_data_processing = sample[field_name]
          data = []
          current_data = {}
          for term in Sample_data_processing:

            # ignoring lines that contain only '*'
            if not term.strip('*'):
              continue

            if term[-1] == ":":
              prev_term = term

            elif ":" in term and not "http:" in term and not "ftp:" in term:
              splited_term = term.split(': ', 1)

              if current_data.has_key(splited_term[0]):
                data.append(current_data)
                current_data = {}

              if len(splited_term) is 2:
                current_data[splited_term[0]] = splited_term[1]
              prev_term = ""

            else:
              if len(prev_term):
                if current_data.has_key(prev_term):
                  data.append(current_data)
                  current_data = {}
                current_data[prev_term] = term
                prev_term = ""

          if current_data:
            data.append(current_data)
          sample[field_name] = data

        else: # Description
          Description = sample[field_name]
          current_data = {}
          for term in Description:

            # ignoring lines that contain only '*'
            if not term.strip('*'):
              continue

            if term[-1] == ":":
              prev_term = term

            elif ":" in term and not "http:" in term and not "ftp:" in term:
              splited_term = term.split(': ', 1)
              if len(splited_term) is 2:
                current_data[splited_term[0]] = splited_term[1]
              prev_term = ""

            else:
              if len(prev_term):
                current_data[prev_term] = term
                prev_term = ""
          sample[field_name] = current_data


  file_metadata["samples"] = samples
  return file_metadata

files = []
def add_file(f):
  files.append(f)

from ftplib import FTP
#print util.download_file('http://ftp.ncbi.nlm.nih.gov/geo/series/GSE16nnn/GSE16256/matrix/', "index.html")

address = "ftp.ncbi.nlm.nih.gov"
path = 'geo/series/GSE16nnn/GSE16256/matrix/'
ftp = FTP(address)
print ftp.login()

ftp.cwd(path)
ftp.retrlines('NLST', add_file)

print files

files_path = "test/"+path
if not os.path.exists(files_path):
  os.makedirs(files_path)

import xmlrpclib
user_key = "Q1LCY43NBZ8Bio1O"
url = "http://localhost:31415"
server = xmlrpclib.Server(url, encoding='UTF-8', allow_none=True)

#set_up_bio_sources(server)
#set_up_samples_fields(server)

total = 0
for file_name in files:
  file_path = files_path+file_name
  file = open(files_path+file_name, 'w')
  ftp.retrbinary('RETR %s' % file_name, file.write)
  file.close()

  pp = pprint.PrettyPrinter(depth=6)
  metadata = process_metadata(files_path+file_name)
  #pp.pprint( metadata['samples'][1] )

  print '#' * 100
  print file_name, len(metadata['samples'])

  for k, roadmap_sample in metadata['samples'].iteritems():
    if type(roadmap_sample['Sample_data_processing']) is not list:
      continue

    #pp.pprint(roadmap_sample)
    total = total + len(roadmap_sample['Sample_data_processing'])

    for experiment in roadmap_sample['Sample_data_processing']:
      if experiment.has_key('ANALYSIS FILE NAME'):
        #print experiment['ANALYSIS FILE NAME']
        continue
      else:
        print '*' * 50
        print roadmap_sample['Sample_supplementary_file_1']
        pp.pprint(experiment)
        pp.pprint(roadmap_sample )
        print '*' * 50

    files = [v for k,v in roadmap_sample.iteritems() if
      type(v) is str and
      k.startswith('Sample_supplementary_file_') and
      (v.endswith("wig.gz") or v.endswith("bed.gz")) ]

    for file_location in files:
      fileinfo, = (info for info in roadmap_sample['Sample_data_processing'] if
        info.has_key("ANALYSIS FILE NAME") and
        info["ANALYSIS FILE NAME"] in file_location)

      print fileinfo

    continue

    sample_info = roadmap_sample['Sample_characteristics_ch1']

    if sample_info['biomaterial_type'] == 'Cell Line':
      bio_source_name = sample_info['line']
    elif sample_info['biomaterial_type'] == 'Primary Tissue':
      bio_source_name = sample_info['tissue_type']
    else:
      pp.pprint(sample_info)
      break
    (s, _ids) = server.get_bio_source_related(bio_source_name, user_key)

    if s == "error":
      print _ids
      pp.pprint(sample_info)

    (s, _id) = server.add_sample(bio_source_name, sample_info, user_key)
    print s
    print _id


print total
