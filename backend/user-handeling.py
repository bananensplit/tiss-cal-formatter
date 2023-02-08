import redis
import string
import random
from typing import Union
from pymongo import MongoClient
from bson.objectid import ObjectId

# TODO: implement encryption




def create_user(username: str, password: str) -> str:
    """Creates a new user in the database and returns the user id"""
    with _get_mongo_connection() as db:
        if (db.find_one({'usernameLower': username.lower()})):
            raise UserAlreadyExistsError()
        result = db.insert_one({
            "username": username,
            "usernameLower": username.lower(),
            "password": password,
        })
        return str(result.inserted_id)


def delete_user(uid: str):
    """Deletes a user from the database"""
    logout_res = logout_user(uid)
    with _get_mongo_connection() as db:
        del_res = db.delete_one({'_id': ObjectId(uid)})
        return del_res.acknowledged


def login_user(username: str, password: str) -> str:
    """Logs in a user and returns the session key"""
    user = _get_user_by_username(username)

    if user is None:
        raise UserDoesNotExistError()

    with _get_redis_connection() as redis:
        session_key = redis.get("uid" + str(user["_id"]))
        
        if session_key is None:
            if user['password'] != password:
                raise UserWrongPasswordError()

            session_key = _gen_session_key()
            redis.set("uid" + str(user["_id"]), "session" + session_key)
            redis.set("session" + session_key, "uid" + str(user["_id"]))

        return session_key


def logout_user(uid: str) -> bool:
    """Logs out a user"""
    with _get_redis_connection() as redis:
        session_key = redis.getdel("uid" + uid)
        user_id = redis.getdel("session" + str(session_key))
        return session_key is not None and user_id is not None


def check_login(uid: str) -> Union[str, None]:
    """Checks if a user is logged in and returns the session key if logged in"""
    with _get_redis_connection() as redis:
        session_key = redis.get("uid" + uid)
        return session_key[7:] if session_key is not None else None


def _get_user_by_uid(uid: str) -> dict:
    """Returns the database entry of a user with the given uid"""
    with _get_mongo_connection() as db:
        return db.find_one({'_id': ObjectId(uid)})


def _get_user_by_username(username: str) -> dict:
    """Returns the database entry of a user with the given username"""
    with _get_mongo_connection() as db:
        return db.find_one({'usernameLower': username.lower()})


def _gen_session_key(length=40) -> str:
    """Generates a random session key"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


# Exceptions
class UserAlreadyExistsError(Exception):
    pass

class UserDoesNotExistError(Exception):
    pass

class UserWrongPasswordError(Exception):
    pass

def main():
    # del_res = delete_user(str(uid))
    # print("Delete result: " + str(del_res))
    
    # Create user
    # uid = create_user("test", "test")
    # print(type(uid))
    # print("Created user with id: " + str(uid))
    
    # session_key = login_user("test", "test")
    # session_key2 = check_login(str(uid))
    # print("Session key:  " + (session_key or "None"))
    # print("Session key2: " + (session_key2 or "None"))
    
    # logout_res = logout_user(str(uid))
    # print("Logout result: " + str(logout_res))
    
    # session_key2 = check_login(str(uid))
    # print("Session key2: " + (session_key2 or "None"))
    
    # # print(login_user("test", "wrong"))
    # print(login_user("wrong", "test"))

    # # Delete user
    # del_res = delete_user(str(uid))
    # print("Delete result: " + str(del_res))
    pass

if __name__ == "__main__":
    main()    