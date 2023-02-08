import pymongo
from pymongo import MongoClient


class MyMongoClient(MongoClient):
    def __init__(self, connection_string, db_name, collection, *args, **kwargs):
        super().__init__(connection_string, *args, **kwargs)
        self.db = self.get_database(db_name)
        self.collection = self.db.get_collection(collection)

    def find_one(self, *args, **kwargs):
        return self.collection.find_one(*args, **kwargs)

    def delete_one(self, *args, **kwargs) -> pymongo.results.DeleteResult:
        return self.collection.delete_one(*args, **kwargs)

    def insert_one(self, *args, **kwargs) -> pymongo.results.InsertOneResult:
        return self.collection.insert_one(*args, **kwargs)
    
    def update_one(self, *args, **kwargs) -> pymongo.results.UpdateResult:
        return self.collection.update_one(*args, **kwargs)

    def check_connection(self) -> bool:
        try:
            self.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            return False
        return True
