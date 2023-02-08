import logging
import random
import string
import hashlib
from pydantic import BaseModel, Field
from pymongo import MongoClient
import redis
from bson.objectid import ObjectId





class User(BaseModel):
    uid: ObjectId = Field(..., alias="_id")
    username: str
    usernameLower: str
    password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UserHandler:
    def __init__(
        self,
        mongo="mongodb://localhost:27017/",
        db_name="tisscal",
        db_user_collection="users",
        redis_host="localhost",
        redis_port=6379,
        redis_password=None,
        logger: logging.Logger = logging.getLogger(__name__),
    ):
        self.logger = logger
        self.client = MongoClient(mongo)
        self.users = self.client[db_name][db_user_collection]
        self.redis = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    def get_user_by_uid(self, uid: str) -> User | None:
        """Gets a user by its uid

        Args:
            uid (str): Id of the user

        Returns:
            User | None: The user or None if the user does not exist
        """
        data = self.users.find_one({"_id": uid})
        return User(**data) if data is not None else None

    def get_user_by_username(self, username: str) -> User | None:
        """Gets a user by its username

        Args:
            username (str): Username of the user

        Returns:
            User | None: The user or None if the user does not exist
        """
        data = self.users.find_one({"usernameLower": username.lower()})
        return User(**data) if data is not None else None

    def login(self, username: str, password: str) -> str | None:
        """Logs in a user and returns a session token

        Args:
            username (str): Username of the user
            password (str): Password of the user

        Raises:
            UserDoesNotExistError: Raised if the user does not exist
            InvalidPasswordError: Raised if the password is incorrect

        Returns:
            str | None: The session token of the user or None if the login failed
        """
        user = self.get_user_by_username(username)
        if user is None:
            raise UserDoesNotExistError()
        if user.password != hashlib.sha256(password.encode()).hexdigest():
            raise InvalidPasswordError()

        if token := self.get_login_session(username=user.username):
            return token[0]

        token = self.generate_login_token()
        self.redis.set(token, str(user.uid))
        self.redis.set(str(user.uid), token)

        return token

    def get_login_session(self, token: str = None, uid: str = None, username: str = None) -> tuple[str] | None:
        """
        Returns the session token and uid of a user if the user is logged in
        Only one of the parameters token, uid or username must be set.

        Args:
            token (str, optional): Given a token retrieves the uid and returns it. Defaults to None.
            uid (str, optional): Given a uid retrieves the session token. Defaults to None.
            username (str, optional): Given a username retrieves token and uid and returns them. Defaults to None.

        Returns:
            tuple(str) | None: The session token and uid of the user or None if the user is not logged in
        """
        if token is not None:
            uid = self.redis.get(token)

        elif uid is not None:
            token = self.redis.get(uid)

        elif username is not None:
            user = self.get_user_by_username(username)
            uid = str(user.uid)
            token = self.redis.get(uid)

        if token is None or uid is None:
            return None

        return (token, uid)

    def is_logged_in(self, token: str = None, uid: str = None, username: str = None) -> bool:
        """Checks if a user is logged in

        Args:
            token (str, optional): Given a token checks if the user is logged in. Defaults to None.
            uid (str, optional): Given a uid checks if the user is logged in. Defaults to None.
            username (str, optional): Given a username checks if the user is logged in. Defaults to None.

        Returns:
            bool: True if the user is logged in, False otherwise
        """
        return self.get_login_session(token, uid, username) is not None

    def logout(self, token: str) -> None:
        """Logs out a user

        Args:
            token (str): The session token of the user
        """
        uid = self.redis.get(token)
        self.redis.delete(token)
        self.redis.delete(uid)

    def logout_all(self):
        self.redis.flushdb()

    def get_all_sessions(self) -> list:
        """Returns all sessions

        Returns:
            list: A list of all sessions
        """
        return [(key, self.redis.get(key)) for key in self.redis.keys()]

    def create_user(self, username: str, password: str) -> User:
        """Creates a new user

        Args:
            username (str): username of the user (must be unique)
            password (str): password of the user

        Raises:
            UserAlreadyExistsError: Raised if a user with the same username already exists

        Returns:
            User: The created user
        """
        usernameLower = username.lower()
        if self.get_user_by_username(usernameLower) is not None:
            raise UserAlreadyExistsError

        result = self.users.insert_one(
            {
                "username": username,
                "usernameLower": usernameLower,
                "password": hashlib.sha256(password.encode()).hexdigest(),
            }
        )

        return User(
            uid=result.inserted_id,
            username=username,
            usernameLower=usernameLower,
            password=password,
        )

    def delete_user_by_uid(self, uid: str):
        """Deletes a user by its uid

        Args:
            uid (str): Id of the user
        """
        if self.get_user_by_uid(uid) is not None:
            self.users.delete_one({"_id": uid})

    def close(self):
        self.logout_all()
        self.client.close()
        self.redis.close()

    @staticmethod
    def generate_login_token(length=30) -> str:
        # characters = string.ascii_letters + string.digits + string.punctuation
        characters = string.ascii_letters + string.digits
        token = "".join(random.choice(characters) for i in range(length))
        return token

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()


# Exceptions
class UserAlreadyExistsError(Exception):
    pass


class UserDoesNotExistError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


def main():
    user_handler = UserHandler(
        "mongodb://admin:adminadmin@10.0.0.150:8882/",
        "tisscal",
        "users",
        "10.0.0.150",
        8881,
        None,
    )
    user_handler.create_user("test", "test")
    user = user_handler.get_user_by_username("test")
    print(user)


if __name__ == "__main__":
    main()
