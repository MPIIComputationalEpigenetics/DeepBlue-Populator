from collections import defaultdict
import csv
from HTMLParser import HTMLParser
import urllib2

def parse_file_name(file_name, mark):
  if not file_name.endswith("gz") and not file_name.endswith('bigwig'): return None
  name, ext = file_name.split(".", 1)

  if (mark == "methylation"):
    eid, emark, ext = name.split("_", 2)
    return eid, emark, file_name
  else:
    eid, emark= name.split("-", 1)
    return eid, emark, file_name

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
        (eid, emark, file_name) = file
        self.__experiments__[eid][emark] = self.__root__ + file_name

experiments = defaultdict(lambda: defaultdict(str))

def parse_data(link):
  (root_address, mark) = link
  parser = MyHTMLParser(root_address, mark, experiments)
  f = urllib2.urlopen(root_address)
  data = f.read()
  print data
  parser.feed(data)

consolidated_narrow_peaks = ("http://egg2.wustl.edu/roadmap/data/byFileType/peaks/consolidated/narrowPeak/",  "peak")
consolidated_broad_peaks = ("http://egg2.wustl.edu/roadmap/data/byFileType/peaks/consolidated/broadPeak/", "peak")
consolidated_signal = ("http://egg2.wustl.edu/roadmap/data/byFileType/signal/consolidated/macs2signal/pval/", "peak") # -log10(p-value)
consolidated_signal_fold_change = ("http://egg2.wustl.edu/roadmap/data/byFileType/signal/consolidated/macs2signal/foldChange/", "peak")
fractional_methylation_wgbs = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/WGBS/FractionalMethylation_bigwig/", "methylation")
read_coverage_wgbs = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/WGBS/ReadCoverage_bigwig/", "methylation")
fractional_methylation_rrbs = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/RRBS/FractionalMethylation_bigwig/", "methylation")
read_coverage_bigwig_rrbs = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/RRBS/ReadCoverage_bigwig/", "methylation")
fractional_methylation_mcrf = ("http://egg2.wustl.edu/roadmap/data/byDataType/dnamethylation/mCRF/FractionalMethylation_bigwig/", "methylation")

sources = (consolidated_narrow_peaks, consolidated_broad_peaks, consolidated_signal, consolidated_signal_fold_change, fractional_methylation_wgbs, read_coverage_wgbs, fractional_methylation_rrbs, read_coverage_bigwig_rrbs, fractional_methylation_mcrf )

for s in sources:
  parse_data(s)

import pprint

pprint.pprint(dict(experiments))


with open('jul2013.roadmapData.qc - Consolidated_EpigenomeIDs_summary_Table.csv', 'r') as csvfile:
  reader = csv.DictReader(csvfile)
  #print reader.fieldnames

  keys = reader.fieldnames

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
