from encode_repository import EncodeRepository
from blueprint_repository import BlueprintRepository
from roadmap_repository import RoadmapRepository
from datasources.local.repository import EpigenomicLandscapeRepository
from log import log


def load(project, genome, url):
    if project == "ENCODE" or project == "Mouse ENCODE":
        return EncodeRepository(project, genome, url)
    elif project == "Blueprint Epigenetics":
        return BlueprintRepository(project, genome, url)
    elif project == 'Roadmap Epigenomics':
        return RoadmapRepository(project, genome, url)
    elif project == 'Epigenomic Landscape':
        return EpigenomicLandscapeRepository(project, genome, url)
    elif project == 'DEEP':
        return EpigenomicLandscapeRepository("DEEP - Deutsches Epigenom Programm", genome, url)
    else:
        log.error("Invalid project %s", project)