from __future__ import absolute_import

from attribute_mapper import AttributeMapper


class IhecDataPortalMapper(AttributeMapper):

    def __init__(self, dataset):
        super(IhecDataPortalMapper, self).__init__(dataset)

    @property
    def name(self):
        file_full_name = self.dataset.file_name.split("/")[-1]
        return ".".join(file_full_name.split(".")[:-1])

    @property
    def epigenetic_mark(self):
        em = self.dataset.meta['epigenetic_mark']
        if em == "RNA-Seq":
            return "RNA"

        if em == "smRNA-Seq":
            return "smRNA"

        if em == "mRNA-Seq":
            return "mRNA"

        if em == "ChIP-Seq Input":
            return "Input"

        if em == "ATAC-Seq":
            return "DNA Accessibility"

        if em.startswith("Histone "):
            return em.split()[1]

        return em

    @property
    def technique(self):
        t = self.dataset.meta['technique']

        if not t:
            epigenetic_mark = self.epigenetic_mark.lower()

            if epigenetic_mark == "mrna":
                return "mRNA-seq"

            if epigenetic_mark == "rna":
                return "RNA-seq "

            if epigenetic_mark == "smrna":
                return "smRNA-seq"

            if epigenetic_mark in ["input", "h3k4me1", "h3k4me3", "h3k27ac", "h3k36me3", "h3k9me3", "h3k27me3"]:
                return "ChIP-seq"

            if epigenetic_mark == "dna methylation":
                if "wgbs" in self.dataset.file_name.lower():
                    return "WGBS"

            if epigenetic_mark == "dna accessibility":
                return self.dataset.meta['epigenetic_mark']

        else:
            t = t.lower()
            if t == "rna-seq assay":
                return "RNA-seq"

            if t == "cross-linking immunoprecipitation high-throughput sequencing assay":
                return "ChIP-seq"

            if t == "shotgun bisulfite-seq assay":
                return "Shotgun bisulfite-seq"

            return t

    @property
    def project(self):
        return self.dataset.meta["project"]

    @property
    def format(self):
        if self.dataset.type in ["signal_unstranded", "methylation_profile", "signal_forward", "signal_reverse"]:
            return 'wig'

        print 'unknow data type: ', self.dataset.type

        return None

    @property
    def genome(self):
        genome = self.dataset.meta["genome"]

        if genome == "hg38":
            return "GRCh38"

        return genome

    @property
    def extra_metadata(self):
        return self.dataset.meta["extra_metadata"]
