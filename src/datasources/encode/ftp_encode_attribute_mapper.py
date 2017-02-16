from __future__ import absolute_import

from attribute_mapper import AttributeMapper

### Many of the mapping used here (in fact, we use only the HMM/Segmentation data mapping, the rest I just keep for 'just in case')

_antibodyToTarget = {
    "H3K36me3B": "H3K36me3",
    "PLU1": "KDM5B",
    "p300": "EP300",
    "P300": "EP300",
    "JMJD2A": "KDM4A",
    "CBP": "CREBBP",
    "Pol2(b)": "POLR2A",
    "JARID1A": "KDM5A",
    "NCoR": "NCOR1",
    "LSD1": "KDM1A",
    "NSD2": "WHSC1",
    "PCAF": "KAT2B",
    "H3K4me3B": "H3K4me3",
    "H3K9acB": "H3K9ac",
    "H3K27me3B": "H3K27me3",
    "c-Jun": "JUN",
    "c-Myb": "MYB",
    "c-Myc": "MYC",
    "COREST": "RCOR1",
    "GCN5": "KAT2A",
    "MyoD": "MYOD1",
    "Myogenin": "MYOG",
    "NELFe": "RDBP",
    "Nrf2": "GABPA",
    "NRSF": "REST",
    "Pol2": "POLR2A",
    "Pol2-4H8": "POLR2A",
    "Pol2(phosphoS2)": "POLR2A",
    "UBF": "UBTF",
    "ZNF-MIZD-CP1": "ZMIZ1",
    "RevXlinkChromatin": "Control",
    "ERRA": "ESRRA",
    "AP-2gamma": "TFAP2C",
    "ERalpha_a": "ESR1",
    "AP-2alpha": "TFAP2A",
    "BAF155": "SMARCC1",
    "BAF170": "SMARCC2",
    "Brg1": "SMARCA4",
    "CDP": "CUX1",
    "GABP": "GABPA",
    "GR": "NR3C1",
    "Ini1": "SMARCB1",
    "NFKB": "RELA",
    "PAX5-C20": "PAX5",
    "PAX5-N19": "PAX5",
    "PGC1A": "PPARGC1A",
    "PU.1": "SPI1",
    "Pol3": "POLR3G",
    "SPT20": "FAM48A",
    "TBLR1": "TBL1XR1",
    "TCF7L2_C9B9": "TCF7L2",
    "TFIIIC-110": "GTF3C2",
    "TR4": "NR2C2",
    "WHIP": "WRNIP1",
    "c-Fos": "FOS"
}

def antibodyToTarget(antibody):
    """Returns the target-name for an antibody-name used in ENCODE"""
    if antibody in _antibodyToTarget:
        return _antibodyToTarget[antibody]
    else:
        return None


class FtpEncodeMapper(AttributeMapper):
    """
    EncodeMapper is the basic AttributeMapper for ENCODE repositories.
    """
    def __init__(self, dataset):
        super(FtpEncodeMapper, self).__init__(dataset)

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
    def format(self):
        return self.dataset.meta["type"]

    @property
    def project(self):
        return "ENCODE"

class FtpEncodeRrbsMethylationMapper(FtpEncodeMapper):
    """
    EncodeMethylationMapper is the AttributeMapper for ENCODE repositories with
    Methylation.
    """
    def __init__(self, dataset):
        super(FtpEncodeRrbsMethylationMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        return "DNA Methylation"

    @property
    def technique(self):
        return "RRBS"


class FtpEncodeMethyl450KMapper(FtpEncodeMapper):
    def __init__(self, dataset):
        super(FtpEncodeMethyl450KMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        return "DNA Methylation"

    @property
    def technique(self):
        return "Infinium 450k"


class FtpEncodeHistoneMapper(FtpEncodeMapper):
    """
    EncodeHistoneMapper is the AttributeMapper for ENCODE repositories with
    histone modification.
    """
    def __init__(self, dataset):
        super(FtpEncodeHistoneMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        antibody = self.dataset.meta["antibody"]
        if "_(" in antibody:
            antibody = antibody.split("_(")[0]
        else:
            antibody = antibody
        target = antibodyToTarget(antibody)
        if target is None:
            return antibody
        else:
            return target

    @property
    def technique(self):
        return "ChIPseq"


class FtpEncodeDNaseIMapper(FtpEncodeMapper):
    def __init__(self, dataset):
        super(FtpEncodeDNaseIMapper, self).__init__(dataset)

    @property
    def technique(self):
        return "DNaseSeq"

    @property
    def epigenetic_mark(self):
        return "DNaseI"


class FtpEncodeDNaseIUniformMapper(FtpEncodeMapper):
    def __init__(self, dataset):
        super(FtpEncodeDNaseIUniformMapper, self).__init__(dataset)

    @property
    def technique(self):
        return "DNaseSeq Uniform"

    @property
    def epigenetic_mark(self):
        return "DNaseI"


class FtpEncodeHMMMapper(FtpEncodeMapper):
    def __init__(self, dataset):
        super(FtpEncodeHMMMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        return "Chromatin State Segmentation"

    @property
    def technique(self):
        return "Chromatin State Segmentation by ChromHMM"


class FtpEncodeTfbsMapper(FtpEncodeMapper):
    def __init__(self, dataset):
        super(FtpEncodeTfbsMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        antibody = self.dataset.meta["antibody"]
        if "_(" in antibody:
            antibody = antibody.split("_(")[0]
        else:
            antibody = antibody
        target = antibodyToTarget(antibody)
        if target is None:
            return antibody
        else:
            return target

    @property
    def technique(self):
        return "ChIPseq"


class FtpEncodeTfbsUniformMapper(FtpEncodeMapper):
    def __init__(self, dataset):
        super(FtpEncodeTfbsUniformMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        antibody = self.dataset.meta["antibody"]
        if "_(" in antibody:
            antibody = antibody.split("_(")[0]
        else:
            antibody = antibody
        target = antibodyToTarget(antibody)
        if target is None:
            return antibody
        else:
            return target

    @property
    def technique(self):
        return "ChIPseq Uniform"


ftp_encode_attribute_mapper = {
    "MethylRrbs": FtpEncodeRrbsMethylationMapper,
    "Methyl": FtpEncodeMethyl450KMapper,
    "Histone": FtpEncodeHistoneMapper,
    "Hist": FtpEncodeHistoneMapper,  # only in mm9
    "Dnase": FtpEncodeDNaseIMapper,
    "ChromDnase": FtpEncodeDNaseIMapper,
    "Dgf": FtpEncodeDNaseIMapper,  # only in mm9
    "UniPk": FtpEncodeDNaseIUniformMapper,
    "Hmm": FtpEncodeHMMMapper,
    "Tfbs": FtpEncodeTfbsMapper,
    "TfbsUniform": FtpEncodeTfbsUniformMapper
}