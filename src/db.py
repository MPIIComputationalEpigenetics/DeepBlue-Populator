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

def repo_exists(project, path):
    return mdb.repositories.find({"project": project, "path": path}).count() > 0

def repo_save(doc):
    mdb.repositories.save(doc)