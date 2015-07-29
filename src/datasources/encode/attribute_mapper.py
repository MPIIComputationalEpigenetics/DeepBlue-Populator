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
        specie = self.dataset.repository["genome"]
        if specie == "Mus musculus":
            return "mm9"
        elif specie == "Homo sapiens":
            return "hg19"

        return "Unknown specie " + specie
