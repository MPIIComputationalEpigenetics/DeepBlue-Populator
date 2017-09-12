from __future__ import absolute_import
from attribute_mapper import AttributeMapper

class ChipAtlasMapper(AttributeMapper):
    """
    ChipAtlasMapper is the basic AttributeMapper for the ChipAtlas project.
    """
    def __init__(self, dataset):
        super(ChipAtlasMapper, self).__init__(dataset)

    @property
    def name(self):
        return self.dataset.meta["ID"]

    @property
    def epigenetic_mark(self):
        em = self.dataset.meta["antigen"]
        if em == "Input control":
            return "Input"
        elif em == "DNase-Seq":
            return "DNA Accessibility"
        elif em == "H3K9K14ac":
            return "H3K9/14ac"

        return em

    @property
    def technique(self):
        return "ChIP-seq"

    @property
    def format(self):
        t = self.dataset.type
        if t == "bed":
            return "narrowPeak"

        return t

    @property
    def genome(self):
        return self.dataset.meta["genome"]

    @property
    def description(self):
        return self.dataset.meta["title"]

    @property
    def extra_metadata(self):
        return self.dataset.meta

    @property
    def project(self):
        return "ChIP-Atlas"
