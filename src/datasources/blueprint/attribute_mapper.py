from __future__ import absolute_import

from attribute_mapper import AttributeMapper

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

        if e == "flrnaa-seq":
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

        if self.name.find("bs_call") != -1:
            return "blueprint_bs_call"

        if self.dataset.type == "bigwig":
            return "wig"

        if self.dataset.type == "gtf":
            return "gff"

        if self.dataset.type == "gff":
            return "gff"

        if self.epigenetic_mark == "mRNA":
            return "encode_rna"

        if self.epigenetic_mark in ["H3K27me3", "H3K36me3", "H3K9me3", "H3K4me1"]:
            return "broadPeak"

        if self.epigenetic_mark in ["H3K27ac", "H3K4me3", "H3K9/14ac", "H2A.Zac"]:
            return "narrowPeak"

        if self.epigenetic_mark == "DNaseI":
            return "bed"

        print "Unknown format for %s epigenetic mark %s and meta %s" % (
            self.name, self.epigenetic_mark, str(self.dataset.meta))

        return None
