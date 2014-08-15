
encode_source = [
  ## Histone Modifications
  ('ENCODE', "hg19",
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeUwHistone/"),
  ('ENCODE', "hg19",
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeBroadHistone/"),
  ('ENCODE', "hg19",
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeSydhHistone/"),

  # TODO: Uniform Histone Modification

  ## Methylation
  ('ENCODE', "hg19",
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeHaibMethyl450/"),
  ('ENCODE', "hg19",
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeHaibMethylRrbs/"),

  ## DNase
  ('ENCODE', "hg19",
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeOpenChromDnase/"),
  ('ENCODE', "hg19",
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeUwDnase/"),
  ('ENCODE', "hg19",
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeAwgDnaseUniform/"),

  ## HMM Chromatin State Segmetation
  ('ENCODE', 'hg19',
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeBroadHmm/"),

  ## TFBS
  ('ENCODE', 'hg19',
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeAwgTfbsUniform/"),
  ('ENCODE', 'hg19',
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeHaibTfbs/"),
  ('ENCODE', 'hg19',
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeSydhTfbs/"),
  ('ENCODE', 'hg19',
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeUchicagoTfbs/"),
  ('ENCODE', 'hg19',
    "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeUwTfbs/"),
]

blueprint_source = [
  ('Blueprint Epigenetics', "hg19", "ftp://ftp.ebi.ac.uk/pub/databases/")
]

roadmap_source = [
  # UCSD Human Reference Epigenome Mapping Project
  ('Roadmap Epigenomics', 'hg19',
    'http://ftp.ncbi.nlm.nih.gov/geo/series/GSE16nnn/GSE16256/matrix/')
]

project_sources = [
  blueprint_source,
  encode_source,
  roadmap_source
]
