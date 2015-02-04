class UnmappedAttribute(Exception):
    """
    UnmappedAttribute exception is raised if for a certain AttributeMapper
    no way to retrieve the attribute is defined.
    """
    def __init__(self, attr):
        super(UnmappedAttribute, self).__init__()
        self.attr = attr

    def __str__(self):
        return "%s is not mapped" % self.attr


class AttributeMapper(object):
    """
    AttributeMapper is a base class for all other mappers. It defines the basic
    attributes which have to be provided for dataset in a repository.
    """
    def __init__(self, dataset):
        self.dataset = dataset

    @property
    def name(self):
        raise UnmappedAttribute("name")

    @property
    def genome(self):
        return self.dataset.repository["genome"]

    @property
    def epigenetic_mark(self):
        raise UnmappedAttribute("epigenetic_mark")

    @property
    def biosource(self):
        raise UnmappedAttribute("biosource")

    @property
    def technique(self):
        raise UnmappedAttribute("technique")

    @property
    def project(self):
        return self.dataset.repository["project"]

    @property
    def description(self):
        return ""

    @property
    def extra_metadata(self):
        return self.dataset.meta

    @property
    def format(self):
        raise UnmappedAttribute("format")