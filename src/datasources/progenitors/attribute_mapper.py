from __future__ import absolute_import

from attribute_mapper import AttributeMapper

class ProgenitorsMapper(AttributeMapper):
    """
    RoadmapMapper is the basic AttributeMapper for Geo repositories.
    """
    def __init__(self, dataset):
        super(ProgenitorsMapper, self).__init__(dataset)

    @property
    def name(self):
        file_full_name = self.dataset.file_name.split("/")[-1]
        return ".".join(file_full_name.split(".")[:-1])

    @property
    def epigenetic_mark(self):
        return self.dataset.meta['epigenetic_mark']

    @property
    def technique(self):
        return self.dataset.meta['technique']

    @property
    def project(self):
        return "BLUEPRINT Progenitors"

    @property
    def format(self):
        return "wig"

    @property
    def extra_metadata(self):
        return self.dataset.meta["extra_metadata"]
