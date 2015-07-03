from __future__ import absolute_import

from attribute_mapper import AttributeMapper

class GeoMapper(AttributeMapper):
    """
    GeoMapper is the basic AttributeMapper for Geo repositories.
    """
    def __init__(self, dataset):
        super(GeoMapper, self).__init__(dataset)

    @property
    def name(self):
        return self.dataset.meta['experiment_name']

    @property
    def epigenetic_mark(self):
        em = self.dataset.meta['epigenetic_mark']
        if em == 'mRNA-Seq':
            return 'mRNA'
        return em

    @property
    def technique(self):
        technique = self.dataset.meta['technique']
        if (technique == 'mRNA-Seq'):
            return 'RNA-Seq'
        return technique

    @property
    def project(self):
        return self.dataset.repository["project"]

    @property
    def format(self):
        return "wig"

    @property
    def extra_metadata(self):
        return self.dataset.meta['extra_metadata']