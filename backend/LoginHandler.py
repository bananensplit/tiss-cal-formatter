import string
import random
import redis
from pymongo import MongoClient
from bson.objectid import ObjectId

# For Testing:
#  Mongo DB access: root:rootPassword
#  Redis access: no password


class LoginHandler():
    # Idea for the future: make session database in redis
    # Idea for the future: allow to store other info than username and password (name, surname, email, ...)

    def __init__(self, connection_string: str, db_name: str, db_user_collection: str, redis_host: str, redis_port: int, redis_password: str) -> None:
        self.connection_string = connection_string
        self.client = MongoClient(connection_string)
        self.db = self.client.get_database(db_name)
        self.users = self.db.get_collection(db_user_collection) # Collection where the users are stored
        self.redis = redis.Redis(host=redis_host, port=redis_port, password=redis_password) # Collection where the session-keys for logged in useres are stored

    @classmethod
    def create_from_info(cls, db_user, db_pass, db_host, db_name, db_user_collection, redis_host, redis_port, redis_password):
        return cls(f"mongodb://{db_user}:{db_pass}@{db_host}/", db_name, db_user_collection, redis_host, redis_port, redis_password)

    def get_all_user_ids():
        pass

    def create_user(self, username, password, **kwargs) -> str:
        # TODO: check if user already exists
        # TODO: check if username format is valid (no spaces, no "ä"/"ö"/"ü"...)
        # TODO: check if password is strong enough

        if (self.users.find_one({'usernameLower': username.lower()})):
            raise UserAlreadyExistsError()

        result = self.users.insert_one({
            "username": username,
            "usernameLower": username.lower(),
            "password": password,
            **kwargs,
        })
        return result.inserted_id
    
    def get_user_info(self, uid):
        return self.users.find_one({'_id': ObjectId(uid)})
    
    def delete_user(self, uid: str) -> bool:
        # Logout user
        logout_res = self.logout_user(uid)
        
        # Delete user
        del_res = self.users.delete_one({'_id': ObjectId(uid)})
        return del_res.acknowledged

    def check_login(self, uid) -> bool:
        return False
 
    def login_user(self, username, password) -> str:
        user = self.users.find_one({'usernameLower': username.lower()})
        
        if user is not None and user['password'] == password:
            session_key = self._generate_session_key()
            self.redis.set(session_key, user['_id'])
            return session_key
        return False
    
    def logout_user(self, uid) -> bool:
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.client.close()

    @staticmethod
    def _generate_session_key(length=30):
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))


class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass



def main():
    login_handler = LoginHandler.create_from_info("root", "rootPassword", "10.0.0.150:27017", "tisscal", "users", "10.0.0.150", 6379, "")
    result_id = login_handler.create_user("Kurwsaa", "Jebem", name="Kurwsa", surname="Jebem")
    print(result_id)
    print(type(result_id))
    login_handler.delete_user(result_id)
    print(login_handler.delete_user('6362c822deaac9a6fd23e621'))
    # login_handler.delete_user("ich habe deine Mutter hops genommen")


if __name__ == "__main__":
    main()