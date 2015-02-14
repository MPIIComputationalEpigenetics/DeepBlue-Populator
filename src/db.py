from pymongo import MongoClient

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


def repo_exists(project, path, genome=None, data_types=None):
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

def repo_remove(project, path, genome=None, data_types=None):
    """Removes all repositories which match the given criteria
    """
    to_remove = {
        "project": project,
        "path": path
    }
    if genome:
        to_remove["genome"] = genome
    if data_types:
        to_remove["data_types"] = data_types

    mdb.repositories.remove(to_remove)

def repo_save(doc):
    mdb.repositories.save(doc)