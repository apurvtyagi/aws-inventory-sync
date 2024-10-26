from pymongo import MongoClient

def connect_mongo(uri):
    client = MongoClient(uri)
    return client

def insert_data(client, database, collection, data):
    db = client[database]
    coll = db[collection]
    coll.delete_many({})
    if data:
        coll.insert_many(data)
