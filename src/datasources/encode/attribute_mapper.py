from __future__ import absolute_import

from attribute_mapper import AttributeMapper


class EncodeMapper(AttributeMapper):
    """
    EncodeMapper is the basic AttributeMapper for ENCODE repositories.
    """
    def __init__(self, dataset):
        super(EncodeMapper, self).__init__(dataset)

    @property
    def name(self):
        file_full_name = self.dataset.file_name.split("/")[-1]
        file_type = file_full_name.split(".")[-1]
        if file_type == "gz":
            return ".".join(file_full_name.split(".")[:-2])
        else:
            return ".".join(file_full_name.split(".")[:-1])

    @property
    def description(self):
        return self.dataset.meta["description"]

    @property
    def format(self):
        return self.dataset.type

    @property
    def epigenetic_mark(self):
        return self.dataset.meta["epigenetic_mark"]

    @property
    def technique(self):
        return self.dataset.meta["technique"]

    @property
    def extra_metadata(self):
        return self.dataset.meta["extra_metadata"]

    @property
    def genome(self):
        return self.dataset.meta["extra_metadata"]["assembly"]

    @property
    def format(self):
        file_type = self.dataset.meta["extra_metadata"]["file_type"]

        if file_type[:3] == "bed" or file_type[:6] == "bigBed":
            _, bed_format = file_type.split()
            if bed_format == "narrowPeak":
                return "narrowPeak"
            if bed_format == "broadPeak":
                return "broadPeak"
            if bed_format == "bed12" or bed_format == "bed9" or bed_format == "bed3":
                return "bed"
            if bed_format == "bedRnaElements":
                return "encode_rna"
            if bed_format == "bedMethyl":
                return "bed"

        print "type not found: " + file_type
        return file_type
