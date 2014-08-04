import os.path
import re
import urllib
import util
import traceback
import threading

from dataset import Dataset
from settings import max_threads
from log import log
from db import mdb
from repository import Repository

"""
A Repository refers to a source of datasets belonging to a certain project.
It detects the available datasets in the repository and can coordinate their
retrival and processing.
"""
class EncodeRepository(Repository):

  def __init__(self, proj, genome, path, user_key):
    super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed", "bigWig"], path, user_key)
    #super(EncodeRepository, self).__init__(proj, genome, ["bigWig"], path, user_key)

  def __str__(self):
    return "<ENCODE Repository: [%s, %s]>" % (self.path, self.data_types)

  """
  index_path is the path to the file which contains information of all
  datasets in the repository.
  """
  @property
  def index_path(self):
    return os.path.join(self.path, "files.txt")

  @property
  def id(self):
    idl = mdb.repositories.find_one({
      "project": self.project, "path": self.path}, ["_id"])
    if not idl:
      return None
    return idl["_id"]

  """
  read_datasets analyses the repositorie's index file and flags
  new datasets.
  """
  def read_datasets(self):
    epigeneticMark = None

    new = 0
    f = urllib.urlopen(self.index_path)
    for line in f:
      s = line.strip().split(None, 1)
      file_name, meta_s = s[0], s[1]

      meta = {}
      for kv in meta_s.split("; "):
        fs = kv.split("=")
        meta[fs[0]] = fs[1]

      if not meta.has_key("dataType"):
        log.info("Line %s from %s does not have datatype" %(line, self.path))
        continue

      r = re.findall('[A-Z][a-z]*', meta["composite"])

      em = r[-1]
      if r[-2] not in ["Haib", "Sydh", "Broad", "Uw", "Uchicago"]:
        em = r[-2] + r[-1]

      if epigeneticMark == None:
        epigeneticMark = em
      elif epigeneticMark != None and epigeneticMark != em:
        print "datatype was set %s but new is %s" %(epigeneticMark, em)

      meta["epigenetic_mark"] = epigeneticMark

      if epigeneticMark == "Histone" and meta["antibody"].find("_") != -1:
          meta["antibody"] = meta["antibody"].split("_")[0]

      # TODO: get sample_id here and remove bio_sample from the attribute_mapper

      size = meta["size"]
      suf = size[-1].lower()
      value = float(size[:-1])

      if (suf == 'k'):
        s = value * 1024
      elif (suf == 'm'):
        s = value * 1024 * 1024
      elif (suf == 'g'):
        s = value * 1024 * 1024 * 1024
      else:
        s = value

      meta["size"] = s

      epigenetic_marks = [
        'h3k4me1', 'h3k4me2', 'h3k4me3', 'h3k9ac', 'h3k9me1', 'h3k27ac', 'h3k27me3', 'h3k36me3', 'h4k20me1',
        'input', 'sp1', 'sp2', 'sp4', 'cmyc', 'nanog', 'pou5f1', 'ezh2', 'suz12', 'e2f1', 'p300', 'ctcf', 'pol2',
        "CTCF_(SC-5916)", "SP2_(SC-643)", "SP4_(V-20)", "CTCF_(SC-15914)", "Control", "CTCFL_(SC-98982)",
        "CTCF_(SC-15914)", "p300_(SC-48343)", "p300_(SC-584)", "EZH2_(39875)", "CTCF", "E2F1", "EZH2",
        "H3K27ac", "H3K27me3", "H3K27me3B","H3K4me1", "H3K4me2", "H3K4me3", "H3K4me3B", "H3K9ac", "H3K9acB",
        "H3K9me1", "H4K20me1", "HA-E2F1", "Input", 'NANOG_(SC-33759)', 'POU2F2' , 'POU5F1_(SC-9081)' ,
        'SUZ12' , 'P300' , 'Pol2' , 'Pol2(b)' , 'Pol2(phosphoS2)' , 'Pol2-4H8' , 'SP1' , 'c-Myc', 'H3K36me3',
        'H3K36me3B'

              ]

      cell_types = [
        'k562', 'gm12878', 'h1hesc', 'hepg2', 'hmec', 'hsmm', 'huvec', 'nhek', 'nhlf', 'h1-hesc',
      ]

      # They were verified. Are cell types and epigenetic marks that will not be used.
      verified = [
          "Dnase", "Rad21", "RevXlinkChromatin", "USF1_(SC-8983)", "YY1_(SC-281)",
          "ChromDnase", "UniPk", "Hmm", "Methyl",
          "eGFP-FOS", "eGFP-GATA2", "eGFP-JunB", "eGFP-JunB",
          "eGFP-JunD", "eGFP-NR4A1", "H3K9me3", "eGFP-FOS", "eGFP-GATA2", "eGFP-HDAC8",
          "eGFP-NR4A1", "ERalpha_a", "FOXA1_(SC-6553)", "GATA3_(SC-268)", "JunD",
          "MethylRrbs", "E2F6", "AP-2alpha", "AP-2gamma", "ARID3A_(NB100-279)",
          "ARID3A_(sc-8821)", "ATF1_(06-325)", "ATF2_(SC-81188)", "ATF3", "BAF155",
          "BAF170", "BATF","BCL11A", "BCL3","BCLAF1_(SC-101388)", "BDP1", "BHLHE40",
          "BHLHE40_(NB100-1800)", "BRCA1_(A300-000A)", "BRCA1_(A300-000A)",
          "BRF1", "BRF2", "Bach1_(sc-14700)", "Brg1", "CBP", "CBX2", "CBX3",
          "CTCFL_(SC-98982)", "GATA-2", "GATA1_(SC-266)", "GATA2_(SC-267)", "GATA3_(SC-269)",
          "GCN5", "GR", "GRp20", "GTF2B", "GTF2F1_(AB28179)", "H2A.Z",
          "CBX3_(SC-101004)", "CBX8", "CCNT2","CDP_(sc-6327)", "CEBPB", "CEBPB_(SC-150)",
          "CEBPD_(SC-636)", "CEBPZ", "CHD1","CHD1_(A301-218A)", "CHD1_(NB100-60411)",
          "CHD2_(AB68301)", "CHD4", "CHD7", "COREST_(ab24166)", "COREST_(sc-30189)",
          "CREB1_(SC-240)", "CtBP2", "E2F4", "EBF1_(SC-137065)", "ELF1_(SC-631)",
          "ELK1_(1277-1)", "ELK4","ERRA", "ETS1",
          "Egr-1", "FOSL1_(SC-183)", "FOSL2", "FOXA1_(SC-101058)", "FOXA2_(SC-6554)",
          "FOXM1_(SC-502)", "FOXP2", "GABP", "GATA-1",
          "TCF12", "TCF3_(SC-349)", "TCF7L2", "TCF7L2_C9B9_(2565)",
          "TEAD4_(SC-101184)", "TFIIIC-110", "THAP1_(SC-98174)",
          "TR4", "TRIM28_(SC-81411)", "UBF_(sc-13125)", "UBTF_(SAB1404509)",
          "HCFC1_(NB100-68209)", "HDAC1", "HDAC1_(SC-6298)", "HDAC2",
          "HDAC2_(A300-705A)", "HDAC2_(SC-6296)", "HDAC6", "HDAC6_(A301-341A)",
          "HEY1", "HMGN3", "HNF4A", "HNF4A_(SC-8987)", "HNF4G_(SC-6558)",
          "HSF1", "IKZF1_(IkN)_(UCLA)", "IRF1", "IRF3", "IRF4_(SC-6059)",
          "Ini1", "JARID1A", "JARID1A_(ab26049)", "JMJD2A", "KAP1",
          "LSD1", "MAZ_(ab85725)", "MBD4_(SC-271530)", "MEF2A", "MEF2C_(SC-13268)",
          "MTA3_(SC-81325)", "MYBL2_(SC-81192)", "MafF_(M8194)", "MafK_(SC-477)",
          "MafK_(ab50322)", "Max", "Mxi1_(AF4185)", "H3K79me2",
          'NCoR' , 'NELFe' , 'NF-E2' , 'NF-E2_(SC-22827)' , 'NF-YA' , 'NF-YB',
          'NFATC1_(SC-17834)' , 'NFIC_(SC-81335)' , 'NFKB' , 'NR2F2_SC-271940)' , 'NRSF' , 'NSD2' ,
          'Nrf1' , 'PAX5-C20' , 'PAX5-N19' , 'PCAF' , 'PGC1A' , 'PHF8' , 'PHF8_(A301-772A)' ,
          'PLU1', 'PML_(SC-71910)' , 'PRDM1_(9115)' , 'PU.1' , 'Pbx3' , 'Pol3' , 'RBBP5' ,
          'RBBP5_(A300-109A)' , 'REST' , 'RFX5_(200-401-194)' , 'RNF2' , 'RPC155' ,
          'RUNX3_(SC-101553)' , 'RXRA' , 'SAP30' , 'SAP30_(39731)' , 'SETDB1' , 'SIN3A_(NB600-1263)' ,
          'SIRT6' , 'SIX5' , 'SMC3_(ab9263)' , 'SPT20' , 'SREBP1' , 'SREBP2' , 'SRF' ,
          'STAT1' , 'STAT2' , 'STAT3' , 'STAT5A_(SC-74442)' , 'Sin3Ak-20' , 'TAF1' , 'TAF7_(SC-101167)' ,
          'TAL1_(SC-12984)' , 'TBLR1_(NB600-270)' , 'TBLR1_(ab24550)' , 'TBP' , 'USF-1' , 'USF2' ,
          'WHIP' , 'XRCC4' , 'YY1' , 'ZBTB33' , 'ZBTB7A_(SC-34508)' , 'ZC3H11A_(NB100-74650)' ,
          'ZEB1_(SC-25388)' , 'ZKSCAN1_(HPA006672)' , 'ZNF-MIZD-CP1_(ab65767)' , 'ZNF217' , 'ZNF263' , 'ZNF274' ,
          'ZNF274_(M01)' , 'ZNF384_(HPA004051)' , 'ZZZ3', 'Znf143_(16618-1-AP)', 'c-Fos', 'c-Jun',
          'NR2F2_(SC-271940)',

          # cell lines
          "a549", "ag04449", "ag04450", "ag09309", "ag09319", "ag10803",
          "aoaf", "be2_c", "bj", "caco-2", "cd20+_ro01778", "cd20+_ro01794",
          "gm06990", "gm12864", "gm12865", "gm12866", "gm12875",
          "h7-hesc", "hac", "ha-sp", "hbmec", "hcf",
          "hcfaa", "hcm", "hcpepic", "hct-116", "hek293", "hela-s3", "hff",
          "hff-myc", "hl-60", "hmf", "hpaf","hpf",  "hre", "hrpepic",  "hvmf",
          "jurkat", "lncap", "mcf-7", "monocytes-cd14+_ro01746", "nb4",
          "nhdf-neo", "panc-1", "rptec", "saec", "skmc", "sk-n-mc", "sk-n-sh_ra",
          "weri-rb-1", "wi-38", "heepic", "a549", "cd20+", "dnd41", "ecc-1",
          "fibrobl", "gliobla",
          "gm08714", "gm10847", "gm12801", "gm12867", "gm12868", "gm12869", "gm12870",
          "gm12871", "gm12872", "gm12873", "gm12874", "gm12891", "gm12892", "gm15510",
          "gm18505", "gm18526", "gm18951", "gm19099", "gm19193", "gm19238", "gm19239", "gm19240",
          "hek293", "hsmmtube", "imr90",
          "imr90", "mcf10a-er-src","nh-a", "nhdf-ad", "nt2-d1",
          "osteobl", "pbde", "pbdefetal", "pbmc", "progfib", "raji",
          "sh-sy5y", "sk-n-sh", "t-47d", "u2os", "hek293-t-rex",
          'a549','ag04449','ag04450','ag09309','ag09319','ag10803','aoaf','be2_c',
          'bj','caco-2','cd20+','cd20+_ro01778','cd20+_ro01794',
          'dnd41','ecc-1','fibrobl','gliobla','gm06990','gm08714',
          'gm10847','gm12801','gm12864','gm12865','gm12866','gm12867','gm12868',
          'gm12869','gm12870','gm12871','gm12872','gm12873','gm12874','gm12875',
          'gm12891','gm12892','gm15510','gm18505','gm18526','gm18951','gm19099',
          'gm19193','gm19238','gm19239','gm19240','h1-neurons','h7-hesc','ha-sp','hac',
          'hbmec','hcf','hcfaa','hcm','hcpepic','hct-116','heepic','hek293',
          'hek293-t-rex','hela-s3','hff','hff-myc','hl-60','hmf','hpaf','hpf',
          'hre','hrpepic','hsmmtube','hvmf','imr90','jurkat','lncap',
          'mcf-7','mcf10a-er-src','monocytes-cd14+_ro01746','nb4','nh-a',
          'nhdf-ad','nhdf-neo','nt2-d1','osteobl','panc-1','pbde',
          'pbdefetal','pbmc','pfsk-1','progfib','raji','rptec',
          'saec','sh-sy5y','sk-n-mc','sk-n-sh','sk-n-sh_ra',
          'skmc','t-47d', 'u2os', 'u87', 'weri-rb-1', 'wi-38'
        ]

      if epigeneticMark not in ["Tfbs", "Histone", "TfbsUniform"]:
        if epigeneticMark not in verified :
          print "Ignoring Epigenetic Mark ", epigeneticMark

        continue

      if not meta.has_key("antibody"):
        print "antibody metadata not found", str(meta)
        continue

      if  meta["antibody"] not in epigenetic_marks:
        if meta["antibody"] not in verified:
          print "ignoring because antibody '" + meta["antibody"] + "' not included"
        continue

      if meta['cell'].lower() not in cell_types:
        if meta['cell'].lower() not in verified:
          print "ignoring because cell line '" + meta["cell"].lower() + "' not included"
        continue

      ds = Dataset(file_name, meta["type"], meta)
      self.datasets.add(ds)
      new +=1

    log.info("found %d new datasets in %s", new, self)
