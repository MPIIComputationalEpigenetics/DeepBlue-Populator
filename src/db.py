from pymongo import MongoClient

import settings

"""
Globals
"""

_client = MongoClient(settings.MDB_HOST, settings.MDB_PORT)
mdb = _client.populator