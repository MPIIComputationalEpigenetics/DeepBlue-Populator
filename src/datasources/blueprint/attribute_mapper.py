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
            return "DNA Accessibility"

        if e == "mrna-seq":
            return "mRNA"

        if e == "flrna-seq":
            return "flRNA"

        if e == "total-rna-seq":
            return "RNA"
        return e

    @property
    def technique(self):
        t = self.dataset.meta["LIBRARY_STRATEGY"].lower()
        e = self.dataset.meta["EXPERIMENT_TYPE"].lower()

        if t == "dnase-hypersensitivity":
            return "DNase-Seq"

        if t == "rna-seq" and e == "total-rna-seq":
            return "total-RNA-seq"

        return t

    @property
    def format(self):
        if self.dataset.type.lower() == "bigwig":
            return "wig"

        if self.dataset.type.lower() == "gtf":
            return "gff"

        if self.dataset.type.lower() == "gff":
            return "gff"

        if self.epigenetic_mark.lower() == "mrna":
            return "encode_rna"

        if self.epigenetic_mark.lower() in ["h3k27me3", "h3k36me3", "h3k9me3", "h3k4me1"]:
            return "broadPeak"

        if self.epigenetic_mark.lower() in ["h3k27ac", "h3k4me3", "h3k9/14ac", "h2a.zac"]:
            return "narrowPeak"

        if self.epigenetic_mark == "DNA Accessibility":
            return "bed"

        if self.dataset.type == "bed" and self.epigenetic_mark.lower() == "dna methylation" and self.technique == "bisulfite-seq":
            return "blueprint_bs_call"

        msg = "Unknown format for %s epigenetic mark %s and meta %s" % (
            self.name, self.epigenetic_mark, str(self.dataset.meta))
        log.critical(msg)

        return None
