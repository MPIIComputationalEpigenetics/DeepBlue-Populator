from __future__ import absolute_import

from attribute_mapper import AttributeMapper

from log import log

class BlueprintMapper(AttributeMapper):
    """
    BlueprintMapper is the basic AttributeMapper for Blueprint repositories.
    """
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
        e = self.dataset.meta["EXPERIMENT_TYPE"].lower()
        if e == "ribo minus rna sequencing":
            return "mRNA"

        if e == "chromatin accessibility":
            return "DNaseI"

        if e == "mrna-seq":
            return "mRNA"

        if e == "flrna-seq":
            return "flRNA"
        return e

    @property
    def technique(self):
        t = self.dataset.meta["LIBRARY_STRATEGY"].lower()
        if t == "dnase-hypersensitivity":
            return "DNase-Seq"

        return t

    @property
    def format(self):
        if self.dataset.type == "bigwig":
            return "wig"

        if self.dataset.type == "gtf":
            return "gff"

        if self.dataset.type == "gff":
            return "gff"

        if self.epigenetic_mark == "mrna":
            return "encode_rna"

        if self.epigenetic_mark in ["h3k27me3", "h3k36me3", "h3k9me3", "h3k4me1"]:
            return "broadPeak"

        if self.epigenetic_mark in ["h3k27ac", "h3k4me3", "h3k9/14ac", "h2a.zac"]:
            return "narrowPeak"

        if self.epigenetic_mark == "dnaseI":
            return "bed"

        msg = "Unknown format for %s epigenetic mark %s and meta %s" % (
            self.name, self.epigenetic_mark, str(self.dataset.meta))
        log.critical(msg)

        return None
