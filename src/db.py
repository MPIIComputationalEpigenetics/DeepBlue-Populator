from pymongo import MongoClient


from log import log
import settings

"""
Globals
"""

_client = MongoClient(settings.MDB_HOST, settings.MDB_PORT)
mdb = _client.populator

def find_not_inserted(id, data_types):
    return mdb.datasets.find({"$and": [
        {"repository_id": id},
        {"type": {"$in": data_types}},
        {"$or": [
            {"inserted": False},
            {"inserted": {"$exists": False}}]}
    ]})

def count_unimported(id, data_types):
    return mdb.datasets.find({
        "$and": [
            {"repository_id": id},
            {"type": {"$in": data_types}},
            {"$or": [
                {"inserted": False},
                {"inserted": {"$inserted": False}}]}
        ]}).count() > 0

def repo_id(project, path):
    return mdb.repositories.find_one({"project": project, "path": path}, ["_id"])


def repo_exists(project, path, genome = None, data_types = None):
    """Checks whether a repository with given parameters exists in DB
    """
    search_for = {
        "project": project,
        "path": path
    }
    if genome:
        search_for["genome"] = genome
    if data_types:
        search_for["data_types"] = data_types

    return mdb.repositories.find(search_for).count() > 0


def repo_save(repository):
    """Saves repository to DB
    :param repository: Repository to save
    """
    doc = {
        "project": repository.project,
        "genome": repository.genome,
        "data_types": repository.data_types,
        "path": repository.path
    }

    if repository.id:
        doc["_id"] = repository.id

    mdb.repositories.save(doc)
    log.debug("saving repository: %s", doc)


def repo_update(repository):
    """Updates the data_type field for project
    :param repository: Repository to update
    """
    mdb.repositories.update({
            "project": repository.project,
            "path": repository.path,
            "genome" : repository.genome
        },
        {
            "$set" : {
                "data_types" : repository.data_types
            }
        })