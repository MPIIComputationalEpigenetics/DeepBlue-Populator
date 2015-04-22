from __future__ import absolute_import

from datasources.geo.attribute_mapper import GeoMapper
from datasources.blueprint.attribute_mapper import BlueprintMapper
from datasources.encode.attribute_mapper import encode_mappers
from datasources.roadmap.attribute_mapper import RoadmapMapper

def get(project, epigenetic_mark=None):
  if project == "ENCODE" or project == "Mouse ENCODE":
    return encode_mappers[epigenetic_mark]
  if project == "GEP":
    return GeoMapper
  if project == "Blueprint Epigenetics":
    return BlueprintMapper
  if project == "Roadmap Epigenomics":
    return RoadmapMapper
  print 'Invalid Project:', project
