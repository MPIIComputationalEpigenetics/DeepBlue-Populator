from __future__ import absolute_import

from attribute_mapper import AttributeMapper


class DEEPMapper(AttributeMapper):
    """
    EncodeMapper is the basic AttributeMapper for ENCODE repositories.
    """
    def __init__(self, dataset):
        super(DEEPMapper, self).__init__(dataset)

    @property
    def name(self):
        file_full_name = self.dataset.file_name.split("/")[-1]
        file_type = file_full_name.split(".")[-1]
        if file_type == "gz":
            return ".".join(file_full_name.split(".")[:-2])
        else:
            return ".".join(file_full_name.split(".")[:-1])

    def NOMe_epigenetic_mark(self):
        if "GCH" in self.name:
            if "peaks" in self.name:
                return "nome_open_chromatin_peaks"

            if "filtered" in self.name:
                return "nome_open_chromatin"

#            else:
#                return "nome_open_chromatin_peaks"

        if "HCG" in self.name:
            return "deep_dna_methylation_calls_bisnp"

        else:
            return "UNKNOWN"


    @property
    def format(self):
        # LOOK AT THE FILE NAME ------
        if self.technique.lower() == "nome-seq":
            return self.NOMe_epigenetic_mark()

        if self.technique.lower() == "wgbs" and "cpg.filtered.CG" in self.name:
                return "deep_dna_methylation_calls_bisnp"

        return self.dataset.type

    @property
    def epigenetic_mark(self):
        if self.technique.lower() == "nome-seq":
            if "deep_dna_methylation_calls_bisnp" == self.NOMe_epigenetic_mark():
                return "DNA Methylation"
            if "nome_open_chromatin" in self.NOMe_epigenetic_mark():
                return "DNA Accessibility"
            else:
                return "UNKNOWN"
        return self.dataset.meta["EPIGENETIC_MARK"]

    @property
    def technique(self):
        return self.dataset.meta["TECHNOLOGY"]

    @property
    def extra_metadata(self):
        return self.dataset.meta["extra"]

    @property
    def genome(self):
        return self.dataset.meta["GENOME"]
