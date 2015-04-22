from __future__ import absolute_import

from attribute_mapper import AttributeMapper

class RoadmapMapper(AttributeMapper):
    """
    RoadmapMapper is the basic AttributeMapper for Geo repositories.
    """
    def __init__(self, dataset):
        super(RoadmapMapper, self).__init__(dataset)

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
        return self.dataset.meta['epigenetic_mark']

    @property
    def technique(self):
        return self.dataset.meta['technique']

    @property
    def project(self):
        return self.dataset.repository["project"]

    @property
    def format(self):
        return self.dataset.meta["type"]

    @property
    def extra_metadata(self):
        return self.dataset.meta["extra"]