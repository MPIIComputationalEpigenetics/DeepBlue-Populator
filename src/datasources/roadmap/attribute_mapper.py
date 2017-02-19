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
        return ".".join(file_full_name.split(".")[:-1])

    @property
    def epigenetic_mark(self):
        em =  self.dataset.meta['epigenetic_mark']
        if em == "Methylation":
            return "DNA Methylation"
        if em == "DNase":
            return "DNaseI"
        if em == "ChrHMM":
            return "Chromatin State Segmentation"
        return em

    @property
    def technique(self):
       t = self.dataset.meta['technique']
       if t == "mCRF":
          return "MeDIP/MRE"
       if t == "ChrHMM":
            return "Chromatin State Segmentation by ChromHMM"
       return t

    @property
    def project(self):
        return self.dataset.repository["project"]

    @property
    def format(self):
        return self.dataset.meta["type"]

    @property
    def extra_metadata(self):
        return self.dataset.meta["extra"]
