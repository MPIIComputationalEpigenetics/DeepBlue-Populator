from blueprint_repository import BlueprintRepository
from datasources.local.repository import EpigenomicLandscapeRepository
from encode_repository import EncodeRepository
from encode_repository import EncodeRepository
from encode_repository_ftp import EncodeRepositoryFTP
from geo_repository import GeoRepository
from roadmap_repository import RoadmapRepository
from deep_repository import DeepRepository
from progenitors_repository import ProgenitorsRepository

from log import log

def load(project, genome, url):
    if project == "ENCODE" or project == "Mouse ENCODE":
        return EncodeRepository(project, genome, url)
    if project == "ENCODE FTP":
        return EncodeRepositoryFTP(project, genome, url)
    elif project == "BLUEPRINT Epigenome":
        return BlueprintRepository(project, genome, url)
    elif project == 'GEO':
        return GeoRepository(project, genome, url)
    elif project == 'Epigenomic Landscape':
        return EpigenomicLandscapeRepository(project, genome, url)
    elif project == 'DEEP':
        return DeepRepository("DEEP", genome, url)
    elif project == "Roadmap Epigenomics":
        return RoadmapRepository("Roadmap Epigenomics", genome, url)
    elif project == "Blueprint HSC differentiation":
        return ProgenitorsRepository("Blueprint HSC differentiation", genome, url)
    else:
        log.error("Invalid project %s", project)
