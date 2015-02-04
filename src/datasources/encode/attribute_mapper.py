from __future__ import absolute_import

from attribute_mapper import AttributeMapper
from datasources.encode.vocabulary import antibodyToTarget


class EncodeMapper(AttributeMapper):
    """
    EncodeMapper is the basic AttributeMapper for ENCODE repositories.
    """
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
    def format(self):
        return self.dataset.meta["type"]


class EncodeRrbsMethylationMapper(EncodeMapper):
    """
    EncodeMethylationMapper is the AttributeMapper for ENCODE repositories with
    Methylation.
    """
    def __init__(self, dataset):
        super(EncodeRrbsMethylationMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        return "DNA Methylation"

    @property
    def technique(self):
        return "RRBS"


class EncodeMethyl450KMapper(EncodeMapper):
    def __init__(self, dataset):
        super(EncodeMethyl450KMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        return "DNA Methylation"

    @property
    def technique(self):
        return "Infinium 450k"


class EncodeHistoneMapper(EncodeMapper):
    """
    EncodeHistoneMapper is the AttributeMapper for ENCODE repositories with
    histone modification.
    """
    def __init__(self, dataset):
        super(EncodeHistoneMapper, self).__init__(dataset)

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


class EncodeDNaseIMapper(EncodeMapper):
    def __init__(self, dataset):
        super(EncodeDNaseIMapper, self).__init__(dataset)

    @property
    def technique(self):
        return "DNaseSeq"

    @property
    def epigenetic_mark(self):
        return "DNaseI"


class EncodeDNaseIUniformMapper(EncodeMapper):
    def __init__(self, dataset):
        super(EncodeDNaseIUniformMapper, self).__init__(dataset)

    @property
    def technique(self):
        return "DNaseSeq Uniform"

    @property
    def epigenetic_mark(self):
        return "DNaseI"


class EncodeHMMMapper(EncodeMapper):
    def __init__(self, dataset):
        super(EncodeHMMMapper, self).__init__(dataset)

    @property
    def epigenetic_mark(self):
        return "Chromatin State Segmentation"

    @property
    def technique(self):
        return "Chromatin State Segmentation by HMM"


class EncodeTfbsMapper(EncodeMapper):
    def __init__(self, dataset):
        super(EncodeTfbsMapper, self).__init__(dataset)

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


class EncodeTfbsUniformMapper(EncodeMapper):
    def __init__(self, dataset):
        super(EncodeTfbsUniformMapper, self).__init__(dataset)

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


encode_mappers = {
    "MethylRrbs": EncodeRrbsMethylationMapper,
    "Methyl": EncodeMethyl450KMapper,
    "Histone": EncodeHistoneMapper,
    "Hist": EncodeHistoneMapper,  # only in mm9
    "Dnase": EncodeDNaseIMapper,
    "ChromDnase": EncodeDNaseIMapper,
    "Dgf": EncodeDNaseIMapper,  # only in mm9
    "UniPk": EncodeDNaseIUniformMapper,
    "Hmm": EncodeHMMMapper,
    "Tfbs": EncodeTfbsMapper,
    "TfbsUniform": EncodeTfbsUniformMapper
}