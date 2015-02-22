import gzip
import os
import os.path
import pprint

from ftplib import FTP

from epidb_interaction import PopulatorEpidbClient
from dataset import Dataset
from repository import Repository
from settings import DOWNLOAD_PATH

pp = pprint.PrettyPrinter(depth=6)

class RoadmapRepository(Repository):

  def __init__(self, proj, genome, path, user_key):
    super(RoadmapRepository, self).__init__(proj, genome, ["wig"], path, user_key)

  def __str__(self):
    return "<Roadmap Repository: [%s, %s]>" % (self.path, self.data_types)

  @property
  def index_path(self):
    return self.path


  def set_up_project(self, server, user_key):
    print server.add_project("Roadmap Epigenomics", "", user_key)

  def set_up_biosources(self,server, user_key):
    (s, r) = server.set_biosource_synonym('Stomach', "Gastric", user_key)
    if s != 'okay' and not r.startswith('104400'): print r

    (s, r) = server.add_biosource('Induced pluripotent stem cell line derived from foreskin fibroblasts', 'Induced pluripotent stem cell. Described by Yu, J. et al. Human induced pluripotent stem cells free of vector and transgene sequences. Science 324, 797-801 (2009).', {"source": "Roadmap Epigenomics"}, user_key)
    if s != 'okay' and not r.startswith('104001'): print r
    (s, r) = server.set_biosource_parent('Induced pluripotent stem cell', 'Induced pluripotent stem cell line derived from foreskin fibroblasts', user_key)
    if s != 'okay' and not r.startswith('104901'): print r

    (s, r) = server.add_biosource('iPS DF 19.11 Cell Line', None, {"source": "Roadmap Epigenomics"}, user_key)
    if s != 'okay' and not r.startswith('104001'): print r
    (s, r) = server.set_biosource_synonym('iPS DF 19.11 Cell Line', 'iPS 19.11', user_key)
    if s != 'okay' and not r.startswith('104400'): print r
    (s, r) = server.set_biosource_synonym('iPS DF 19.11 Cell Line', 'iPS DF 19.11', user_key)
    if s != 'okay' and not r.startswith('104400'): print r
    (s, r) = server.set_biosource_parent('Induced pluripotent stem cell line derived from foreskin fibroblasts', 'iPS DF 19.11 Cell Line', user_key)
    if s != 'okay' and not r.startswith('104901'): print r

    (s, r) = server.add_biosource('iPS DF 6.9 Cell Line', None, {"source": "Roadmap Epigenomics"}, user_key)
    if s != 'okay' and not r.startswith('104001'): print r
    (s, r) = server.set_biosource_synonym('iPS DF 6.9 Cell Line', 'iPS 6.9', user_key)
    if s != 'okay' and not r.startswith('104400'): print r
    (s, r) = server.set_biosource_synonym('iPS DF 6.9 Cell Line', 'iPS DF 6.9', user_key)
    if s != 'okay' and not r.startswith('104400'): print r
    (s, r) = server.set_biosource_parent('Induced pluripotent stem cell line derived from foreskin fibroblasts', 'iPS DF 6.9 Cell Line', user_key)
    if s != 'okay' and not r.startswith('104901'): print r

    (s, r) = server.add_biosource('hSKM', "HSkM-S (Cat. no. A12555) are normal human skeletal myoblasts developed to undergo highly efficient differentiation directly following plating of cryopreserved cells.", {"source": "Roadmap Epigenomics", "more_info":"http://tools.lifetechnologies.com/content/sfs/manuals/HSkM_S.pdf"}, user_key)
    if s != 'okay' and not r.startswith('104001'): print r
    (s, r) = server.set_biosource_parent('HSMM', 'hSKM', user_key)
    if s != 'okay' and not r.startswith('104901'): print r

  def process_matrix_file(self, _file):
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


  def read_datasets(self):
    user_key = self.user_key
    files = []
    def add_file(f):
      files.append(f)

    address = "ftp.ncbi.nlm.nih.gov"
    data_path = self.path.split(address)[1]

    ftp = FTP(address)
    print ftp.login()

    ftp.cwd(data_path)
    ftp.retrlines('NLST', add_file)

    print files

    files_path = DOWNLOAD_PATH+"/roadmap_matrix/"+data_path
    if not os.path.exists(files_path):
      os.makedirs(files_path)

    server = PopulatorEpidbClient()
    self.set_up_project(server, self.user_key)
    self.set_up_biosources(server, self.user_key)
    self.set_up_samples_fields(server, self.user_key)

    total = 0
    for file_name in files:
      print 'Downloading', file_name
      file_path = files_path+file_name
      file = open(files_path+file_name, 'w')
      ftp.retrbinary('RETR %s' % file_name, file.write)
      file.close()

      metadata = self.process_matrix_file(files_path+file_name)

      for k, roadmap_sample in metadata['samples'].iteritems():

        if type(roadmap_sample['Sample_data_processing']) is not list:
          continue

        epigenetic_mark = ""
        if roadmap_sample['Sample_characteristics_ch1'].has_key('chip_antibody'):
          epigenetic_mark = roadmap_sample['Sample_characteristics_ch1']['chip_antibody']

        elif roadmap_sample['Sample_characteristics_ch1'].has_key('chip_protocol'):
          epigenetic_mark = roadmap_sample['Sample_characteristics_ch1']['chip_protocol']

        elif roadmap_sample['Sample_characteristics_ch1'].has_key('bisulfite_conversion_protocol'):
          epigenetic_mark = roadmap_sample['Sample_characteristics_ch1']['experiment_type']

        elif roadmap_sample['Sample_characteristics_ch1'].has_key('experiment_type'):
          epigenetic_mark = roadmap_sample['Sample_characteristics_ch1']['experiment_type']

        else:
          pp.pprint(roadmap_sample)
          print '*' * 1000
          break

        sample_info = roadmap_sample['Sample_characteristics_ch1']
        sample_metada = {}
        sample_experiment_metadata = {}
        sample_experiment_metadata['experiment_type'] = sample_info['experiment_type']
        del sample_info['experiment_type']

        for k in sample_info:
          if sample_info[k] != 'NA' and sample_info[k] != 'N/A' and sample_info[k] != 'None' and not k == 'molecule' and not k.startswith('extraction_protocol') and not k.startswith('chip_protocol') and not k.startswith('chip_antibody') and not k.startswith('dna_preparation_') and not k.startswith('library_generation') and not k.startswith('rna_preparation_') and not k.startswith('mrna_preparation') and not k.startswith('bisulfite_conversion') and not k.startswith('cdna_preparation'):
            sample_metada[k] = sample_info[k]
          else:
            if sample_info[k] != 'NA' and sample_info[k] != 'N/A' and sample_info[k] != 'None':
              sample_experiment_metadata[k] = sample_info[k]

        if sample_info['biomaterial_type'] == 'Cell Line':
          biosource_name = sample_metada['line']
        elif sample_info['biomaterial_type'] == 'Primary Tissue':
          biosource_name = sample_metada['tissue_type']
        else:
          pp.pprint(sample_metada)
          break
        (s, _ids) = server.get_biosource_related(biosource_name)

        if s == "error":
          print _ids
          pp.pprint(sample_metada)

        (s, sample_id) = server.add_sample(biosource_name, sample_metada)

        files = [v for k,v in roadmap_sample.iteritems() if
          type(v) is str and
          k.startswith('Sample_supplementary_file_') and
          (v.endswith("wig.gz"))] #  or v.endswith("bed.gz")) if we are going to import bed files

        for file_path in files:
          fileinfo, = (info for info in roadmap_sample['Sample_data_processing'] if
            info.has_key("ANALYSIS FILE NAME") and
            info["ANALYSIS FILE NAME"] in file_path)

          extra_metadata = dict(
            dict((k.replace(".", ""), v) for k, v in fileinfo.items()).items() +
            dict((k.replace(".", ""), v) for k, v in sample_experiment_metadata.items()).items() +
            dict((k.replace(".", ""), v) for k, v in roadmap_sample.items() if type(v) is str).items()
          )

          count = 1
          while True:
            if extra_metadata.has_key('Sample_supplementary_file_%d' %(count)):
              del extra_metadata['Sample_supplementary_file_%d' %(count)]
              count = count + 1
            else:
              break

          extra_metadata['file_path'] = file_path

          meta = {}
          meta['experiment_name'] = fileinfo['ANALYSIS FILE NAME']
          meta['epigenetic_mark'] = epigenetic_mark
          meta['technique'] = fileinfo['EXPERIMENT_TYPE']
          meta['description'] = fileinfo['ANALYSIS DESCRIPTION']
          meta['extra_metadata'] = extra_metadata


          ds = Dataset(file_path, "wig", meta, sample_id=sample_id)
          if self.add_dataset(ds):
            total += 1
            self.has_updates = True
    print total
