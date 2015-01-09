from attribute_mapper import AttributeMapper

class EpigenomicLandscapeAttributeMapper(AttributeMapper):
    def __init__(self, dataset):
        super(self.__class__, self).__init__(dataset)

    @property
    def name(self):
        return self.dataset.meta["name"]

    @property
    def genome(self):
        return self.dataset.repository["genome"]

    @property
    def epigenetic_mark(self):
        if (self.dataset.meta["epigenetic_mark"] == "DNA methylation"):
            return "Methylation"
        return self.dataset.meta["epigenetic_mark"]

    @property
    def biosource(self):
        return self.dataset.meta["biosource"]

    @property
    def technique(self):
        return self.dataset.meta["technique"]

    @property
    def project(self):
        return self.dataset.meta["project"]

    @property
    def description(self):
        return self.dataset.meta["description"]

    @property
    def extra_metadata(self):
        return self.dataset.meta

    @property
    def format(self):
        return self.dataset.meta["format"]

