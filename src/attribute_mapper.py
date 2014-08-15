
"""
UnmappedAttribute exception is raised if for a certain AttributeMapper
no way to retrieve the attribute is defined.
"""
class UnmappedAttribute(Exception):
  def __init__(self, attr):
    super(UnmappedAttribute, self).__init__()
    self.attr = attr

  def __str__(self):
    return "%s is not mapped" % self.attr


"""
AttributeMapper is a base class for all other mappers. It defines the basic
attributes which have to be provided for dataset in a repository.
"""
class AttributeMapper(object):
  def __init__(self, dataset):
    self.dataset = dataset

  @property
  def name(self):
    raise UnmappedAttribute("name")

  @property
  def genome(self):
    return self.dataset.repository["genome"]

  @property
  def epigenetic_mark(self):
    raise UnmappedAttribute("epigenetic_mark")

  @property
  def bio_source(self):
    raise UnmappedAttribute("bio_source")

  @property
  def technique(self):
    raise UnmappedAttribute("technique")

  @property
  def project(self):
    return self.dataset.repository["project"]

  @property
  def description(self):
    return ""

  @property
  def format(self):
    raise UnmappedAttribute("format")


"""
BlueprintMapper is the basic AttributeMapper for Blueprint repositories.
"""
class BlueprintMapper(AttributeMapper):

  def __init__(self, dataset):
    super(BlueprintMapper, self).__init__(dataset)

  @property
  def name(self):
    file_full_name = self.dataset.file_name.split("/")[-1]
    file_type = file_full_name.split(".")[-1]
    if file_type == "gz":
      return ".".join(file_full_name.split(".")[:-2])
    else:
      return ".".join(file_full_name.split(".")[:-1])

  @property
  def epigenetic_mark(self):
    e = self.dataset.meta["EXPERIMENT_TYPE"]
    if e == "DNA Methylation":
      return "Methylation"

    if e == "Ribo Minus RNA sequencing":

      return "mRNA-seq"

    if e == "Chromatin Accessibility":
      return "DNaseI"

    return e

  @property
  def technique(self):
    t = self.dataset.meta["LIBRARY_STRATEGY"]
    if t == "DNase-Hypersensitivity":
      return "DNaseSeq"

    return t

  @property
  def format(self):

    if self.name.find("bs_call") != -1:
      return "blueprint_bs_call"

    if self.epigenetic_mark == "mRNA-seq":
      return "encode_rna"

    return "bed"

"""
EncodeMapper is the basic AttributeMapper for ENCODE repositories.
"""
class EncodeMapper(AttributeMapper):

  def __init__(self, dataset):
    super(EncodeMapper, self).__init__(dataset)

  @property
  def name(self):
    if self.dataset.meta.has_key("tableName"):
      return self.dataset.meta["tableName"]

    file_full_name = self.dataset.file_name.split("/")[-1]
    file_type = file_full_name.split(".")[-1]
    if file_type == "gz":
      return ".".join(file_full_name.split(".")[:-2])
    else:
      return ".".join(file_full_name.split(".")[:-1])


  @property
  def bio_source(self):
    return self.dataset.meta["cell"]

  @property
  def format(self):
    return self.dataset.meta["type"]


"""
EncoddeMethylationMapper is the AttributeMapper for ENCODE repositories with
Methylation.
"""
class EncodeRrbsMethylationMapper(EncodeMapper):
  def __init__(self, dataset):
    super(EncodeRrbsMethylationMapper, self).__init__(dataset)

  @property
  def epigenetic_mark(self):
    return "Methylation"

  @property
  def technique(self):
    return "RRBS"

"""
"""
class EncodeMethyl450KMapper(EncodeMapper):
  def __init__(self, dataset):
    super(EncodeMethyl450KMapper, self).__init__(dataset)

  @property
  def epigenetic_mark(self):
    return "Methylation"

  @property
  def technique(self):
    return "Infinium 450k"

"""
EncodeHistoneMapper is the AttributeMapper for ENCODE repositories with
histone modification.
"""
class EncodeHistoneMapper(EncodeMapper):
  def __init__(self, dataset):
    super(EncodeHistoneMapper, self).__init__(dataset)

  @property
  def epigenetic_mark(self):
    return self.dataset.meta["antibody"]

  @property
  def technique(self):
    return "ChipSeq"

"""
"""
class EncodeDNaseIMapper(EncodeMapper):
  def __init__(self, dataset):
    super(EncodeDNaseIMapper, self).__init__(dataset)

  @property
  def technique(self):
    return "DNaseSeq"

  @property
  def epigenetic_mark(self):
    return "DNaseI"

"""
"""
class EncodeDNaseIUniformMapper(EncodeMapper):
  def __init__(self, dataset):
    super(EncodeDNaseIUniformMapper, self).__init__(dataset)

  @property
  def technique(self):
    return "DNaseSeq Uniform"

  @property
  def epigenetic_mark(self):
    return "DNaseI"


"""
"""
class EncodeHMMMapper(EncodeMapper):
  def __init__(self, dataset):
    super(EncodeHMMMapper, self).__init__(dataset)

  @property
  def epigenetic_mark(self):
    return "Chromatin State Segmentation"

  @property
  def technique(self):
    return "Chromatin State Segmentation by HMM"

"""
"""
class EncodeTFBSMapper(EncodeMapper):
  def __init__(self, dataset):
    super(EncodeTFBSMapper, self).__init__(dataset)

  @property
  def epigenetic_mark(self):
    return "TFBS"

  @property
  def technique(self):
    return "ChipSeq"


"""
"""
class EncodeTfbsUniformMapper(EncodeMapper):
  def __init__(self, dataset):
    super(EncodeTfbsUniformMapper, self).__init__(dataset)

  @property
  def epigenetic_mark(self):
    return "TFBS"

  @property
  def technique(self):
    return "ChipSeq Uniform"


"""
RoadmapMapper is the basic AttributeMapper for Roadmap repositories.
"""
class RoadmapMapper(AttributeMapper):

  def __init__(self, dataset):
    super(RoadmapMapper, self).__init__(dataset)

  @property
  def name(self):
    return self.dataset.meta['experiment_name']

  @property
  def epigenetic_mark(self):
    return self.dataset.meta['epigenetic_mark']

  @property
  def technique(self):
    return self.dataset.meta['technique']

  @property
  def project(self):
    return self.dataset.repository["project"]

  @property
  def format(self):
    return "wig"


encode_mappers = {
  ("ENCODE", "MethylRrbs") : EncodeRrbsMethylationMapper,
  ("ENCODE", "Methyl") : EncodeMethyl450KMapper,
  ("ENCODE", "Histone") : EncodeHistoneMapper,
  ("ENCODE", "Dnase") : EncodeDNaseIMapper,
  ("ENCODE", "ChromDnase") :  EncodeDNaseIMapper,
  ("ENCODE", "UniPk") : EncodeDNaseIUniformMapper,
  ("ENCODE", "Hmm") : EncodeHMMMapper,
  ("ENCODE", "Tfbs") : EncodeTFBSMapper,
  ("ENCODE", "TfbsUniform") : EncodeTfbsUniformMapper
}

def do_map(project, epigenetic_mark = None):
  if project == "ENCODE": return encode_mappers(project, epigenetic_mark)
  if project == "Roadmap Epigenomics": return RoadmapMapper
  if project == "Blueprint Epigenetics" : return BlueprintMapper
  print 'Invalid Project:', project
