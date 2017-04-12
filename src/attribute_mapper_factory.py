from __future__ import absolute_import

from datasources.geo.attribute_mapper import GeoMapper
from datasources.blueprint.attribute_mapper import BlueprintMapper
from datasources.deep.attribute_mapper import DEEPMapper
from datasources.encode.attribute_mapper import EncodeMapper
from datasources.encode.ftp_encode_attribute_mapper import ftp_encode_attribute_mapper
from datasources.roadmap.attribute_mapper import RoadmapMapper
from datasources.progenitors.attribute_mapper import ProgenitorsMapper
from datasources.ihec_data_portal.attribute_mapper import IhecDataPortalMapper

def get(project, epigenetic_mark=None):
  if project == "ENCODE":
    return EncodeMapper
  if project == "ENCODE FTP":
    return ftp_encode_attribute_mapper[epigenetic_mark]
  if project == "GEP":
    return GeoMapper
  if project == "BLUEPRINT Epigenome":
    return BlueprintMapper
  if project == "Roadmap Epigenomics":
    return RoadmapMapper
  if project == "DEEP":
    return DEEPMapper
  if project == "Blueprint HSC differentiation":
    return ProgenitorsMapper
  if project in ["CREST"]:
    return IhecDataPortalMapper

  print 'Invalid Project:', project
