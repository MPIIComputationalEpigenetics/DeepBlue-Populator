from __future__ import absolute_import

import re

from attribute_mapper import AttributeMapper

_regex_dp = re.compile("(.*?):(.*)")

class EpigenomicLandscapeAttributeMapper(AttributeMapper):
    def __init__(self, dataset):
        super(self.__class__, self).__init__(dataset)

    @property
    def name(self):
        return self.dataset.meta["name"]

    @property
    def genome(self):
        return self.dataset.meta["genome"]

    @property
    def epigenetic_mark(self):
        return self.dataset.meta["epigenetic_mark"]

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
        _extra_metadata = {}
        for key in self.dataset.meta:
            if key.startswith("extra_metadata"):
                _match_dp = _regex_dp.match(self.dataset.meta[key])
                _extra_metadata[_match_dp.group(1)] = _match_dp.group(2)
        return _extra_metadata

    @property
    def format(self):
        return self.dataset.meta["format"]

