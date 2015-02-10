from password_manager import PROJECT_USER, PROJECT_PASSWORD

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

    ## HMM Chromatin State Segmentation
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
    #('Blueprint Epigenetics', "hg19", "ftp://ftp.ebi.ac.uk/pub/databases/")
    ('Blueprint Epigenetics', "hg19", "ftp://"+PROJECT_USER("blueprint")+":"+PROJECT_PASSWORD("blueprint")+"@ftp.1000genomes.ebi.ac.uk/")
]

roadmap_source = [
    # UCSD Human Reference Epigenome Mapping Project
    ('Roadmap Epigenomics', 'hg19',
     'http://ftp.ncbi.nlm.nih.gov/geo/series/GSE16nnn/GSE16256/matrix/'),

    # UCSF-UBC Human Reference Epigenome Mapping Project
    ('Roadmap Epigenomics', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE16nnn/GSE16368/matrix/'),

    # BI Human Reference Epigenome Mapping Project
    ('Roadmap Epigenomics', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE17nnn/GSE17312/matrix/'),

    # University of Washington Human Reference Epigenome Mapping Project
    ('Roadmap Epigenomics', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE18nnn/GSE18927/matrix/'),

    # BI Human Reference Epigenome Mapping Project: ChIP-Seq in human subject
    ('Roadmap Epigenomics', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE19nnn/GSE19465/matrix/'),

    # BI Human Reference Epigenome Mapping Project: Characterization of DNA methylation by RRBS
    ('Roadmap Epigenomics', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE25nnn/GSE25246/matrix/'),

    # BI Human Reference Epigenome Mapping Project: Characterization of DNA methylation by RRBS in human subject
    ('Roadmap Epigenomics', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE25nnn/GSE25247/matrix/'),

    # BI Human Reference Epigenome Mapping Project: Characterization of DNA methylation by RRBS in HUES lines
    ('Roadmap Epigenomics', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE25nnn/GSE25248/matrix/'),

    # BI Human Reference Epigenome Mapping Project: Characterization of chromatin modification by ChIP-Seq in human subject
    ('Roadmap Epigenomics', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE25nnn/GSE25249/matrix/')
]

encode_mm9 = [
    # histone modifications
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodeCaltechHist/'),
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodeLicrHistone/'),
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodePsuHistone/'),
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodeSydhHist/'),
    # tfbs
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodeCaltechTfbs/'),
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodeLicrTfbs/'),
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodePsuTfbs/'),
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodeSydhTfbs/'),
    # DNase
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodePsuDnase/'),
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodeUwDgf/'),
    ('Mouse ENCODE', 'mm9',
     'http://hgdownload.cse.ucsc.edu/goldenPath/mm9/encodeDCC/wgEncodeUwDnase/')
]

epigenomic_landscape = [
    ('Epigenomic Landscape', 'None',
     '/local/data/DeepBlue-Populator/data/forDeepBlue')
]

deep = [
    ('DEEP', 'None',
     '/local/data/DeepBlue-Populator/data/deep/forDeepBlue')
]

project_sources = [
     # blueprint_source,
     # encode_source
     # encode_mm9,
     # epigenomic_landscape
     deep
     # roadmap_source
]
