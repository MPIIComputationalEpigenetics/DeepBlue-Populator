from __future__ import absolute_import

from datasources.roadmap.attribute_mapper import RoadmapMapper
from datasources.blueprint.attribute_mapper import BlueprintMapper
from datasources.encode.attribute_mapper import encode_mappers

def get(project, epigenetic_mark=None):
    if project == "ENCODE" or project == "Mouse ENCODE":
        return encode_mappers[epigenetic_mark]
    if project == "Roadmap Epigenomics":
        return RoadmapMapper
    if project == "Blueprint Epigenetics":
        return BlueprintMapper
    print 'Invalid Project:', project
