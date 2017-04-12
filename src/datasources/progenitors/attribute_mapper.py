from __future__ import absolute_import

from attribute_mapper import AttributeMapper

class ProgenitorsMapper(AttributeMapper):

    def __init__(self, dataset):
        super(ProgenitorsMapper, self).__init__(dataset)

    @property
    def name(self):
        file_full_name = self.dataset.file_name.split("/")[-1]
        return ".".join(file_full_name.split(".")[:-1])

    @property
    def epigenetic_mark(self):
        em = self.dataset.meta['epigenetic_mark']
        if em == "RNA-Seq":
            return "RNA"
        return em

    @property
    def technique(self):
        t = self.dataset.meta['technique']
        if t == "RNA-seq assay":
            return "RNA-seq"
        return t

    @property
    def project(self):
        return "Blueprint HSC differentiation"

    @property
    def format(self):
        return "wig"

    @property
    def extra_metadata(self):
        return self.dataset.meta["extra_metadata"]
