import hashlib
import logging
import random
import re
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
        redis_expire: int = 10800,
    ):
        self.logger = logger

        self.connection_string = connection_string
        self.db_name = db_name
        self.user_collection = user_collection
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_expire = redis_expire if redis_expire > 0 else None

        self.logger.info("Initializing UserHandler")
        self.logger.debug("    Mongo connection string: %s", self.connection_string)
        self.logger.debug("    Mongo DB name:           %s", self.db_name)
        self.logger.debug("    Mongo collection name:   %s", self.user_collection)
        self.logger.debug("    Redis host:              %s", self.redis_host)
        self.logger.debug("    Redis port:              %s", self.redis_port)
        self.logger.debug("    Redis password:          %s", self.redis_password)
        self.logger.debug("    Redis expire:            %s", self.redis_expire)

        with self._get_mongo_connection() as client:
            if not client.check_connection():
                self.logger.error("While initializing UserHandler: MongoDB connection failed")
                raise Exception("MongoDB connection failed")

        with self._get_redis_connection() as client:
            if not client.ping():
                self.logger.error("While initializing UserHandler: MongoDB connection failed")
                raise Exception("Redis connection failed")

    def get_user_by_uid(self, uid: str) -> UserDB | None:
        """Retrieves a user from the database by its uid

        Arguments:
            uid {str} -- UID of the user

        Returns:
            UserDB | None -- UserDB object if the user was found, None otherwise
        """
        with self._get_mongo_connection() as client:
            data = client.find_one({"_id": ObjectId(uid)})
            self.logger.debug("Getting user by uid: %s\nGot user: %s", uid, data)
            return UserDB(**data) if data is not None else None

    def get_user_by_username(self, username: str) -> UserDB | None:
        """Retrieves a user from the database by its username

        Arguments:
            username {str} -- Username of the user (case insensitive)

        Returns:
            UserDB | None -- UserDB object if the user was found, None otherwise
        """
        with self._get_mongo_connection() as client:
            data = client.find_one({"usernameLower": username.lower()})
            self.logger.debug("Getting user by username: %s\nGot user: %s", username, data)
            return UserDB(**data) if data is not None else None

    def login(self, username: str, password: str) -> str | None:
        """Logs in a user and returns a session token

        Arguments:
            username {str} -- Username of the user
            password {str} -- Password of the user

        Returns:
            str | None -- session token if the login was successful, None otherwise
        """
        self.logger.info("Login: Logging in user %s", username)
        user = self.get_user_by_username(username)

        if user is None:
            self.logger.info("Login failed: User not found: %s", username)
            return None

        if user.password != hashlib.sha256(password.encode()).hexdigest():
            self.logger.info("Login failed: Wrong password for user %s", username)
            return None

        if (session := self.get_session(username=user.username)) is not None:
            self.logger.info("Login: User %s already logged in, returning session token: %s", username, session[0])
            return session[0]

        session_token = self.generate_session_token()
        with self._get_redis_connection() as client:
            client.set(session_token, str(user.uid), ex=self.redis_expire)
            client.set(str(user.uid), session_token, ex=self.redis_expire)
        self.logger.info("Login: User %s logged in, returning session token: %s", username, session_token)

        return session_token

    def logout(self, uid: str) -> bool:
        """Logs out a user by its uid

        Arguments:
            uid {str} -- UID of the user

        Returns:
            bool -- returns True if the user was logged out, False otherwise
        """
        self.logger.info("Logout: Logging out user %s", uid)
        if not self.check_login(uid=uid):
            self.logger.info("Logout: User was never logged in or session already expired: %s", uid)
            return True

        with self._get_redis_connection() as client:
            token = client.get(uid)
            client.delete(uid)
            client.delete(token)
            return True

    def logout_all(self):
        """Logs out all users"""
        with self._get_redis_connection() as client:
            self.logger.info("Logout all: Logging out all users")
            client.flushdb()

    def check_login(self, token: str = None, uid: str = None, username: str = None) -> bool:
        """Checks if a user is logged in / if a session in the database exists with the given token or uid.
        Only one of the arguments should be set. If multiple are set, the first one is used.

        Keyword Arguments:
            token {str} -- token of the login session (default: {None})
            uid {str} -- uid of the logged in user (default: {None})
            username {str} -- username of the logged in user (default: {None})

        Returns:
            bool -- Returns True if the user is logged in (a session exists), False otherwise
        """
        return self.get_session(token, uid, username) is not None

    def refresh_session(self, token: str = None, uid: str = None, username: str = None) -> tuple[str] | None:
        """Refreshes the session of a user. If the user is not logged in, None is returned.
        Only one of the arguments should be set. If multiple are set, the first one is used.

        Keyword Arguments:
            token {str} -- token of the login session (default: {None})
            uid {str} -- uid of the logged in user (default: {None})
            username {str} -- username of the logged in user (default: {None})

        Returns:
            tuple[str] | None -- Returns a tuple of the session token and uid if the user is logged in, None otherwise
        """
        with self._get_redis_connection() as client:
            if token is not None:
                self.logger.debug("Refreshing session by token: %s", token)
                uid = client.get(token)

            elif uid is not None:
                self.logger.debug("Refreshing session by uid: %s", uid)
                token = client.get(uid)

            elif username is not None:
                self.logger.debug("Refreshing session by username: %s", username)
                user = self.get_user_by_username(username)
                if user is not None:
                    uid = str(user.uid)
                    token = client.get(uid)

            if uid is None or token is None:
                self.logger.debug("Refreshing session: Session not found")
                return None

            client.expire(uid, self.redis_expire)
            client.expire(token, self.redis_expire)
            self.logger.debug("Refreshing session: Session refreshed")
            return token

    def get_session(self, token: str = None, uid: str = None, username: str = None) -> tuple[str] | None:
        """Returns the session token and uid of a logged in user. If the user is not logged in, None is returned.
        Only one of the arguments should be set. If multiple are set, the first one is used.

        Keyword Arguments:
            token {str} -- token of the login session (default: {None})
            uid {str} -- uid of the logged in user (default: {None})
            username {str} -- username of the logged in user (default: {None})

        Returns:
            tuple[str] | None -- Returns a tuple of the session token and uid if the user is logged in, None otherwise
        """
        with self._get_redis_connection() as client:
            if token is not None:
                self.logger.debug("Getting session by token: %s", token)
                uid = client.get(token)

            elif uid is not None:
                self.logger.debug("Getting session by uid: %s", uid)
                token = client.get(uid)

            elif username is not None:
                self.logger.debug("Getting session by username: %s", username)
                user = self.get_user_by_username(username)
                if user is not None:
                    uid = str(user.uid)
                    token = client.get(uid)

            if token is None or uid is None:
                self.logger.debug("Session not found")
                return None

            self.logger.debug("Session found (token, uid): %s, %s", token, uid)
            return (token, uid)

    def get_all_sessions(self) -> list:
        """Returns a list of all sessions in the database"""
        with self._get_redis_connection() as client:
            return [(key, client.get(key)) for key in client.keys()]

    def create_user(self, username: str, password: str) -> UserDB | None:
        """Creates a new user in the database and returns the user object

        Arguments:
            username {str} -- Username of the new user
            password {str} -- Password of the new user

        Returns:
            UserDB | None -- Returns the user object if the user was created, None otherwise
        """
        self.logger.info("Creating user: username: %s", username)
        usernameLower = username.lower()

        if re.match(r"^[.a-zA-Z0-9@_-]{8,40}$", username) is None:
            self.logger.info("Creating user failed: Username does not match ^[.a-zA-Z0-9@_-]{8,40}$")
            return None

        if len(password) < 8:
            self.logger.info("Creating user failed: Password is too short (min 8 characters)")
            return None

        if self.get_user_by_username(usernameLower) is not None:
            self.logger.info("Creating user failed: User already exists (%s)", username)
            return None

        with self._get_mongo_connection() as client:
            result = client.insert_one(
                {
                    "username": username,
                    "usernameLower": usernameLower,
                    "password": hashlib.sha256(password.encode()).hexdigest(),
                }
            )

            self.logger.debug("Created user: uid: %s", result.inserted_id)
            return UserDB(
                uid=result.inserted_id,
                username=username,
                usernameLower=usernameLower,
                password=password,
            )

    def check_if_user_exists(self, username: str) -> bool:
        return self.get_user_by_username(username) is not None

    def delete_user_by_uid(self, uid: str):
        """Deletes a user by its uid

        Arguments:
            uid {str} -- UID of the user to delete
        """
        self.logger.info("Deleting user: uid: %s", uid)
        if self.get_user_by_uid(uid) is None:
            self.logger.info("Deleting user: User already doesn't exists (uid: %s)", uid)
            return

        self.logger.info("Deleting user: Logging out user (uid: %s)", uid)
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
        self.logger.info("Closing UserHandler")
        self.logout_all()
