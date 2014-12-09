from encode_repository import EncodeRepository
from blueprint_repository import BlueprintRepository
from roadmap_repository import RoadmapRepository
from log import log


def load(project, genome, url, user_key):
    if project == "ENCODE" or project == "Mouse ENCODE":
        return EncodeRepository(project, genome, url, user_key)
    elif project == "Blueprint Epigenetics":
        return BlueprintRepository(project, genome, url, user_key)
    elif project == 'Roadmap Epigenomics':
        return RoadmapRepository(project, genome, url, user_key)
    else:
        log.error("Invalid project %s", project)