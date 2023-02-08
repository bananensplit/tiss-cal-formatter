from pymongo import MongoClient


class LoginHandler():
    def __init__(self, connection_string, db_name, db_collection) -> None:
        self.connection_string = connection_string
        self.client = MongoClient(connection_string)
        self.db = self.client.get_database(db_name)
        self.collection = self.db.get_collection(db_collection)

    @classmethod
    def create_from_info(cls, db_user, db_pass, db_host, db_name, db_collection):
        return cls(f"mongodb://{db_user}:{db_pass}@{db_host}/", db_name, db_collection)

    def create_new_user(self, username, password) -> str:
        # TODO: check if user already exists
        # TODO: check if username format is valid (no spaces, no "ä"/"ö"/"ü"...)
        # TODO: check if password is strong enough
        result = self.collection.insert_one({
            "username": username,
            "password": password,
        })
        return result.inserted_id

    def get_all_user_ids():
        pass

    def delete_user(self, uid):
        pass

    def check_login(self, username, password) -> dict:
        return {}


def main():
    login_handler = LoginHandler.create_from_info("root", "rootPassword", "192.168.0.100:27017", "tisscal", "users")
    login_handler.create_new_user("Hello", "Jebem")


if __name__ == "__main__":
    main()