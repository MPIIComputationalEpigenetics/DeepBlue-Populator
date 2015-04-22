from blueprint_repository import BlueprintRepository
from datasources.local.repository import EpigenomicLandscapeRepository
from encode_repository import EncodeRepository
from geo_repository import GeoRepository
from roadmap_repository import RoadmapRepository

from log import log

def load(project, genome, url):
    if project == "ENCODE" or project == "Mouse ENCODE":
        return EncodeRepository(project, genome, url)
    elif project == "Blueprint Epigenetics":
        return BlueprintRepository(project, genome, url)
    elif project == 'GEP':
        return GeoRepository(project, genome, url)
    elif project == 'Epigenomic Landscape':
        return EpigenomicLandscapeRepository(project, genome, url)
    elif project == 'DEEP':
        return EpigenomicLandscapeRepository("DEEP - Deutsches Epigenom Programm", genome, url)
    elif project == "Roadmap Epigenomics":
        return RoadmapRepository("Roadmap Epigenomics", genome, url)
    else:
        log.error("Invalid project %s", project)