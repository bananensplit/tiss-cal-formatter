import logging
import random
import string

from bson.objectid import ObjectId

from Lva import Lva
from models.TissCalModels import TissCalDB, TissCalDBCreate
from MyCalendar import MyCalendar
from MyMongoClient import MyMongoClient
from UserHandler import UserHandler


class TissCalHandler:
    def __init__(
        self,
        logger: logging.Logger = logging.getLogger(__name__),
        connection_string: str = "mongodb://localhost:27017",
        db_name: str = "project",
        tiss_cal_collection: str = "calendars",
        user_handler: UserHandler = None,
    ):
        self.logger = logger

        self.connection_string = connection_string
        self.db_name = db_name
        self.tiss_cal_collection = tiss_cal_collection

        self.user_handler = user_handler

        with self._get_mongo_connection() as client:
            if not client.check_connection():
                raise Exception("MongoDB connection failed")

    def create_new_calendar(self, url: str, name: str, owner: str) -> TissCalDB | None:
        # TODO: check if Name is already taken (only for the owner)
        cal = MyCalendar.get_cal_from_url(url)
        if cal is None:
            return None

        if self.user_handler.get_user_by_uid(owner) is None:
            return None

        with self._get_mongo_connection() as client:
            data = TissCalDBCreate(
                url=url,
                name=name,
                owner=owner,
                token=TissCalHandler.generate_calendar_token(),
                all_events=[
                    {
                        "name": event_name,
                        "will_prettify": Lva.is_lva_str(event_name),
                        "will_remove": False,
                        "is_lva": Lva.is_lva_str(event_name),
                    }
                    for event_name in cal.get_distinct_events()
                ],
            ).dict()
            result = client.insert_one(data)

        return TissCalDB(uid=result.inserted_id, **data)
    
    def update_calendar(self, calendar: TissCalDB) -> TissCalDB | None:
        with self._get_mongo_connection() as client:
            result = client.update_one({"_id": calendar.id}, {"$set": calendar.dict()})
            if result.matched_count == 0:
                return None

        return calendar

    def delete_calendar_by_token(self, token: str) -> bool:
        with self._get_mongo_connection() as client:
            result = client.delete_one({"token": token})
            return result.deleted_count == 1

    def get_calendar_by_id(self, id: str) -> TissCalDB | None:
        with self._get_mongo_connection() as client:
            data = client.find_one({"_id": ObjectId(id)})
            return TissCalDB(**data) if data is not None else None

    def get_calendar_by_token(self, token: str) -> TissCalDB | None:
        with self._get_mongo_connection() as client:
            data = client.find_one({"token": token})
            return TissCalDB(**data) if data is not None else None

    def get_calendars_by_owner(self, uid: str) -> list[TissCalDB]:
        with self._get_mongo_connection() as client:
            data = client.find({"owner": uid})
            return [TissCalDB(**d) for d in data]

    def prettify_calendar(self, token: str) -> str | None:
        cal_data = self.get_calendar_by_token(token)
        if cal_data is None:
            return None

        cal = MyCalendar.get_cal_from_url(cal_data.url)
        if cal is None:
            return None

        for event in cal_data.all_events:
            if not event.will_remove:
                continue
            cal.delete_events_by_name(event.name)

        for event in cal_data.all_events:
            if not (event.is_lva and event.will_prettify):
                continue

            location_template = cal_data.templates.get(event.name, cal_data.default_template.defaultLocationFormat)
            description_template = cal_data.templates.get(event.name, cal_data.default_template.defaultDescriptionFormat)
            summary_template = cal_data.templates.get(event.name, cal_data.default_template.defaultSummaryFormat)
            cal.prettify_events_by_name(event.name, location_template, description_template, summary_template)

        return cal.to_ical()

    @staticmethod
    def generate_calendar_token(length=30) -> str:
        # TODO: check if token is unique
        characters = string.ascii_letters + string.digits
        token = "".join(random.choice(characters) for i in range(length))
        return token

    def _get_mongo_connection(self):
        return MyMongoClient(self.connection_string, self.db_name, self.tiss_cal_collection)
