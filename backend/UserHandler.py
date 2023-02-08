import hashlib
import logging
import random
import string

import redis
from bson.objectid import ObjectId

from models.UserModels import UserDB
from MyMongoClient import MyMongoClient


class UserHandler:
    def __init__(
        self,
        logger: logging.Logger = logging.getLogger(__name__),
        connection_string: str = "mongodb://localhost:27017",
        db_name: str = "project",
        user_collection: str = "users",
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: str | None = None,
    ):
        self.logger = logger

        self.connection_string = connection_string
        self.db_name = db_name
        self.user_collection = user_collection
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password

        with self._get_mongo_connection() as client:
            if not client.check_connection():
                raise Exception("MongoDB connection failed")

        with self._get_redis_connection() as client:
            if not client.ping():
                raise Exception("Redis connection failed")

    def get_user_by_uid(self, uid: str) -> UserDB | None:
        with self._get_mongo_connection() as client:
            data = client.find_one({"_id": ObjectId(uid)})
            return UserDB(**data) if data is not None else None

    def get_user_by_username(self, username: str) -> UserDB | None:
        with self._get_mongo_connection() as client:
            data = client.find_one({"usernameLower": username.lower()})
            return UserDB(**data) if data is not None else None

    def login(self, username: str, password: str) -> str | None:
        user = self.get_user_by_username(username)
        if user is None:
            return None

        print(user.password)
        print(password)
        print(hashlib.sha256(password.encode()).hexdigest())

        if user.password != hashlib.sha256(password.encode()).hexdigest():
            return None

        if (session := self.get_session(username=user.username)) is not None:
            return session[0]

        session_token = self.generate_session_token()
        with self._get_redis_connection() as client:
            client.set(session_token, str(user.uid))
            client.set(str(user.uid), session_token)

        return session_token

    def logout(self, uid: str) -> bool:
        if not self.check_login(uid=uid):
            return True

        with self._get_redis_connection() as client:
            token = client.get(uid)
            client.delete(uid)
            client.delete(token)
            return True

    def logout_all(self):
        with self._get_redis_connection() as client:
            client.flushdb()

    def check_login(self, token: str = None, uid: str = None, username: str = None) -> bool:
        return self.get_session(token, uid, username) is not None

    def get_session(self, token: str = None, uid: str = None, username: str = None) -> tuple[str] | None:
        with self._get_redis_connection() as client:
            if token is not None:
                uid = client.get(token)

            elif uid is not None:
                token = client.get(uid)

            elif username is not None:
                user = self.get_user_by_username(username)
                uid = str(user.uid)
                token = client.get(uid)

            if token is None or uid is None:
                return None

            return (token, uid)

    def get_all_sessions(self) -> list:
        with self._get_redis_connection() as client:
            return [(key, client.get(key)) for key in client.keys()]

    def create_user(self, username: str, password: str) -> UserDB:
        usernameLower = username.lower()
        if self.get_user_by_username(usernameLower) is not None:
            raise UserAlreadyExistsError

        with self._get_mongo_connection() as client:
            result = client.insert_one(
                {
                    "username": username,
                    "usernameLower": usernameLower,
                    "password": hashlib.sha256(password.encode()).hexdigest(),
                }
            )

            return UserDB(
                uid=result.inserted_id,
                username=username,
                usernameLower=usernameLower,
                password=password,
            )

    def delete_user_by_uid(self, uid: str):
        if self.get_user_by_uid(uid) is None:
            return

        self.logout(uid=uid)
        with self._get_mongo_connection as client:
            client.delete_one({"_id": uid})

    def generate_session_token(self, length=30) -> str:
        # characters = string.ascii_letters + string.digits + string.punctuation
        characters = string.ascii_letters + string.digits
        token = "".join(random.choice(characters) for i in range(length))
        return token

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _get_mongo_connection(self) -> MyMongoClient:
        return MyMongoClient(self.connection_string, self.db_name, self.user_collection)

    def _get_redis_connection(self) -> redis.Redis:
        return redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password, decode_responses=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def close(self):
        self.logout_all()


# Exceptions
class UserAlreadyExistsError(Exception):
    pass
