from password_manager import PROJECT_USER, PROJECT_PASSWORD

encode = [
    ('ENCODE', "Mus musculus", "https://www.encodeproject.org/"),
    #('ENCODE', "Homo sapiens", "https://www.encodeproject.org/"),
]

blueprint_source = [
     ('BLUEPRINT Epigenome', "hg19", "ftp://ftp.ebi.ac.uk/pub/databases/"),
#    ('BLUEPRINT Epigenome', "hg19", "ftp://"+PROJECT_USER("blueprint")+":"+PROJECT_PASSWORD("blueprint")+"@ftp.1000genomes.ebi.ac.uk/")
]

geo_source = [
    # UCSD Human Reference Epigenome Mapping Project
    ('GEO', 'hg19',
     'http://ftp.ncbi.nlm.nih.gov/geo/series/GSE16nnn/GSE16256/matrix/'),

    # UCSF-UBC Human Reference Epigenome Mapping Project
    ('GEO', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE16nnn/GSE16368/matrix/'),

    # BI Human Reference Epigenome Mapping Project
    ('GEO', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE17nnn/GSE17312/matrix/'),

    # University of Washington Human Reference Epigenome Mapping Project
    ('GEO', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE18nnn/GSE18927/matrix/'),

    # BI Human Reference Epigenome Mapping Project: ChIP-Seq in human subject
    ('GEO', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE19nnn/GSE19465/matrix/'),

    # BI Human Reference Epigenome Mapping Project: Characterization of DNA methylation by RRBS
    ('GEO', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE25nnn/GSE25246/matrix/'),

    # BI Human Reference Epigenome Mapping Project: Characterization of DNA methylation by RRBS in human subject
    ('GEO', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE25nnn/GSE25247/matrix/'),

    # BI Human Reference Epigenome Mapping Project: Characterization of DNA methylation by RRBS in HUES lines
    ('GEO', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE25nnn/GSE25248/matrix/'),

    # BI Human Reference Epigenome Mapping Project: Characterization of chromatin modification by ChIP-Seq in human subject
    ('GEO', 'hg19',
     'ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE25nnn/GSE25249/matrix/')
]

roadmap = [
    ('Roadmap Epigenomics', 'hg19', 'None')
]

epigenomic_landscape = [
    ('Epigenomic Landscape', 'None',
     '/local/data/DeepBlue-Populator/data/forDeepBlue')
]

deep = [
    ('DEEP', 'hs37d5', ''),
    ('DEEP', 'GRCm38mm10', '')
]

project_sources = [
     # roadmap
     # blueprint_source,
     encode
     # encode_mm9,
     # epigenomic_landscape
     # deep
     # geo_source
]
