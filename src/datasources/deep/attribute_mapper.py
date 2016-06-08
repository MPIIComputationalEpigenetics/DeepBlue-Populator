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
        if "GCH" in self.name():
            print "QQ GCH"
            return "nome_open_chromatin_peaks"
        if "HGC" in self.name():
            print "QQ HGC"
            return "deep_dna_methylation_calls_bisnp"
        else:
            print "QQ else"
            return "deep_dna_methylation_calls_bisnp"


    @property
    def format(self):
        # LOOK AT THE FILE NAME ------
        if self.dataset.meta["TECHNOLOGY"].lower() == "NOMe-seq":
            return self.NOMe_epigenetic_mark()

        return self.dataset.type

    @property
    def epigenetic_mark(self):
        if self.dataset.meta["TECHNOLOGY"].lower() == "NOMe-seq":
            if "deep_dna_methylation_calls_bisnp" == self.NOMe_epigenetic_mark():
                return "DNA Accessibility"
            if "nome_open_chromatin_peaks" == self.NOMe_epigenetic_mark():
                return "DNA Methylation"
            else:
                return "DNA methylation"
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
