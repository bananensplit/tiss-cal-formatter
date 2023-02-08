from pymongo import MongoClient
import redis


class MyMongoClient(MongoClient):
    def __init__(self, connection_string, db_name, user_collection, *args, **kwargs):
        super().__init__(connection_string, *args, **kwargs)
        self.db = self.get_database(db_name)
        self.user_collection = self.db.get_collection(user_collection)

    def find_one(self, *args, **kwargs):
        return self.user_collection.find_one(*args, **kwargs)

    def delete_one(self, *args, **kwargs):
        return self.user_collection.delete_one(*args, **kwargs)
        
    def insert_one(self, *args, **kwargs):
        return self.user_collection.insert_one(*args, **kwargs)



def _get_mongo_connection() -> MyMongoClient:
    connection_string = "mongodb://root:rootPassword@10.0.0.150:27017/"
    db_name = "tisscal"         # name of the monogodb database
    user_collection = "users"   # name of the collection where the users are stored
    return MyMongoClient(connection_string, db_name, user_collection)


def _get_redis_connection() -> redis.Redis:
    redis_host = "10.0.0.150"
    redis_port = 6379
    redis_password = ""
    return redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)