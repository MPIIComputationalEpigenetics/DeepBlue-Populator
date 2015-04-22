import util
from dataset import Dataset
from repository import Repository
from epidb_interaction import PopulatorEpidbClient

import csv
import pprint
import urllib2
from collections import defaultdict
from HTMLParser import HTMLParser


"""
A Repository refers to a source of datasets belonging to a certain project.
It detects the available datasets in the repository and can coordinate their
retrival and processing.
"""

def parse_file_name(file_name, mark):
  if not file_name.endswith("gz") and not file_name.endswith('bigwig'): return None

  name, extension = file_name.split(".", 1)

  if (mark == "methylation"):
    eid, emark, ext = name.split("_", 2)
    return eid, emark, ext, file_name
  else:
    eid, emark, = name.split("-", 1)

    if emark == "H2A":
      emark = "H2A.Z"
      s = extension.split(".", 2)
      type_ = s[1]
    else:
      type_, end = extension.split(".", 1)
      #if type_ in ["pval", "fc",

    return eid, emark, type_, file_name

class MyHTMLParser(HTMLParser):
  def __init__(self, root, mark, experiments):
    HTMLParser.__init__(self)
    self.__root__ = root
    self.__mark__ = mark
    self.__experiments__ = experiments

  def handle_starttag(self, tag, attrs):
    if tag == "a":
      file = parse_file_name(attrs[0][1], self.__mark__)
      if file:
        (eid, emark, ext, file_name) = file
        self.__experiments__[eid][emark][ext] = self.__root__ + file_name

def parse_data(link, experiments):
    (root_address, mark) = link
    parser = MyHTMLParser(root_address, mark, experiments)
    f = urllib2.urlopen(root_address)
    data = f.read()
    parser.feed(data)


class RoadmapRepository(Repository):
  def __init__(self, proj, genome, path):
    super(RoadmapRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bigWig"], path)

  def __str__(self):
    return "<Roadmap Epigenomics Repository: [%s, %s]>" % (self.path, self.data_types)

  @property
  def sources(self):
    # Histone data
    consolidated_narrow_peaks = ("http://egg2.wustl.edu/roadmap/data/byFileType/peaks/consolidated/narrowPeak/",  "histones")
    consolidated_broad_peaks = ("http://egg2.wustl.edu/roadmap/data/byFileType/peaks/consolidated/broadPeak/", "histones")
    consolidated_signal = ("http://egg2.wustl.edu/roadmap/data/byFileType/signal/consolidated/macs2signal/pval/", "histones") # -log10(p-value)
    consolidated_signal_fold_change = ("http://egg2.wustl.edu/roadmap/data/byFileType/signal/consolidated/macs2signal/foldChange/", "histones")

    # Methylation data
    fractional_methylation_wgbs = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/WGBS/FractionalMethylation_bigwig/", "methylation")
    read_coverage_wgbs = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/WGBS/ReadCoverage_bigwig/", "methylation")
    fractional_methylation_rrbs = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/RRBS/FractionalMethylation_bigwig/", "methylation")
    read_coverage_bigwig_rrbs = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/RRBS/ReadCoverage_bigwig/", "methylation")
    fractional_methylation_mcrf = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/mCRF/FractionalMethylation_bigwig/", "methylation")

    sources = (consolidated_narrow_peaks, consolidated_broad_peaks, consolidated_signal, consolidated_signal_fold_change, fractional_methylation_wgbs, read_coverage_wgbs, fractional_methylation_rrbs, read_coverage_bigwig_rrbs, fractional_methylation_mcrf )

    return sources

  def samples(self):
    with open('datasources/roadmap/jul2013.roadmapData.qc - Consolidated_EpigenomeIDs_summary_Table.csv', 'r') as csvfile:
      reader = csv.DictReader(csvfile)
      keys = reader.fieldnames

      # Some header as multiple lines. Keep just the first line.
      new_keys = []
      for k in keys:
        if "\n" in k:
          new_keys.append( k.split("\n")[0] )
        else:
          new_keys.append(k)
      reader = csv.DictReader(csvfile, new_keys)

      samples = []
      ids = {}
      reader.next() # header
      reader.next() # sub header

      for line in reader:
        sample_info = {}

        sample_keys = ["Comments", "Epigenome ID (EID)", "GROUP", "COLOR", "Epigenome Mnemonic", "Under Seq", "Quality Rating", "Auto Use Train (Core)", "Manual Use Train (Core)", "Train Core + K27ac", "Standardized Epigenome name", "Epigenome name (from EDACC Release 9 directory)", "ANATOMY", "TYPE", "LAB", "AGE", "SEX", "SOLID / LIQUID", "ETHNICITY", "Single Donor (SD) /Composite (C)", "DONOR / SAMPLE ALIAS", "CLASS"]

        for key in sample_keys:
          if line[key]:
            sample_info[key] = line[key]

        eid = sample_info["Epigenome ID (EID)"]
        ids[eid] = sample_info
        samples.append(sample_info)

      total = 0
      found = 0
      epidb = PopulatorEpidbClient()

      mapped = {}
      for s in samples:
        eid = s["Epigenome ID (EID)"]
        #original_name = biosource_name = s["Epigenome name (from EDACC Release 9 directory)"]
        biosource_name = s["ANATOMY"]

        if biosource_name == "IPSC":
          biosource_name = "induced pluripotent stem cell"
        elif biosource_name == "ESC_DERIVED":
          biosource_name = "embryonic stem cell"
        elif biosource_name == "MUSCLE_LEG":
          biosource_name = "MUSCLE"
        elif biosource_name == "STROMAL_CONNECTIVE":
          if s["Epigenome name (from EDACC Release 9 directory)"] == "Bone_Marrow_Derived_Mesenchymal_Stem_Cell_Cultured_Cells":
            biosource_name = "stromal cell of bone marrow"
          if s["Epigenome name (from EDACC Release 9 directory)"] == "Chondrocytes_from_Bone_Marrow_Derived_Mesenchymal_Stem_Cell_Cultured_Cells":
            biosource_name = "chondrocyte"
        elif biosource_name.startswith("GI_"):
          biosource_name = biosource_name[len("GI_"):]
        if epidb.is_biosource(biosource_name)[0] == "okay":
         # print "found",
          found = found + 1
          #print "inserting sample for ", eid, " under biosource ", biosource_name, "content: ", s
          s["source"] = "Roadmap Epigenomics"
          s, _id = epidb.add_sample(biosource_name, s)
          if s == "okay":
            mapped[eid] = _id
        else:
          print biosource_name, " not mapped"

        total = total + 1

      if total - found > 0:
        print "** Roadmap: Not mapped " , str(total - found), " from ", total

      return mapped


  def build_epigenetic_mark_technique_and_type(self, v1, v2, file):
    if v2 == "broadPeak" or v2 == "narrowPeak":
      return v1, "ChIP-seq", v2

    if v2 == "pval":
      return v1, "ChIP-seq", "bigWig"

    if v2 == "ReadCoverage" or v2 == "FractionalMethylation":
      return "Methylation", v1, "bigWig"

    if v2 == "fc":
      return v1, "ChIP-seq", "bigWig"

    if v1 == "DNase" and v2 == "macs2":
      return v1, "ChIP-seq", "narrowPeak"

    if v1 == "DNase" and v2 == "hotspot":
      return v1, "ChIP-seq", "broadPeak"

    if v1 == "H2A" and v2 == "Z":
      print file
      if "signal" in file:
        return "H2A.Z", "ChIP-seq", "bigWig"


    print "Not found:", v1, v2
    return None, None, None

  def build_metadata(self, eid, sample, v1, v2, file):
    meta = {}
    meta["file"] = file
    meta["genome"] = self.genome
    meta["sample"] = sample
    (epigenetic_mark, technique, type_) = self.build_epigenetic_mark_technique_and_type(v1, v2, file)
    if not technique:
      print file
      return
    meta["epigenetic_mark"] = epigenetic_mark
    meta["technique"] = technique
    meta["type"] = type_
    meta["project"] = "Roadmap Epigenomics"

    extra = {}
    extra["mark"] = v1
    extra["type"] = v2
    extra["url"] = file
    extra["roadmap epigenome"] = eid

    meta["extra"] = extra

    return meta

  """
  read_datasets analyses the repositorie's index file and flags
  new datasets.
  """
  def read_datasets(self):
    new = 0
    samples = self.samples()

    experiments = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
    for s in self.sources:
      parse_data(s, experiments)

    #pprint.pprint(dict(experiments))

    for epigenome in experiments:
      #print epigenome
      for epigenetic_mark in experiments[epigenome]:
        #print " ", epigenetic_mark
        for technique in experiments[epigenome][epigenetic_mark]:
          #print "   ", technique
          #print experiments[epigenome][epigenetic_mark][technique],
          meta = self.build_metadata(epigenome, samples[epigenome], epigenetic_mark, technique, experiments[epigenome][epigenetic_mark][technique])
          #print "      ", str(meta)
          ds = Dataset(meta["file"], meta["type"], meta, sample_id=meta["sample"])
          #print ds

          if self.add_dataset(ds):
            new += 1
            self.has_updates = True


