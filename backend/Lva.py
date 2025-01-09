import csv
import re
import urllib.parse
from functools import cache

from icalendar.cal import Event
from jinja2 import BaseLoader, Environment


@cache
def read_rooms(file="resources/TU-Rooms.csv"):
    # TODO: Maybe move this also to a database
    with open(file, "r", encoding="UTF-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        return [room for room in reader]


def get_room_data(room_name=None):
    if room_name == "":
        return None

    for room in read_rooms():
        if room_name == room[0]:
            return [
                room[0],  # Room Name
                room[8],  # Tiss Link
                f"https://maps.tuwien.ac.at/?q={room[7]}#map",  # TU Wien Maps Link
                room[6].split(",")[0],  # Real World Location
            ]
    else:
        return None


class Lva:
    PROPERTIES_TEMPLATE = [
        "LvaName",
        "LvaTypeShort",
        "LvaTypeLong",
        "LvaId",
        "StartDate",
        "StartTime",
        "EndDate",
        "EndTime",
        "TissCourseDetailLink",
        "TissEducationDetailLink",
        "TissCalDesc",
        "RoomName",
        "RoomTiss",
        "RoomTuwMap",
        "RoomBuildingAddress",
        "Categorie",
    ]

    LVA_TYPE_MAP = {
        "VO": "Vorlesung",
        "VU": "Vorlesung mit Übung",
        "UE": "Übung",
        "AE": "Arbeitsgemeinschaft und Exkursion",
        "AG": "Arbeitsgemeinschaft",
        "AU": "Angeleitete Übung",
        "EP": "Studieneingangsphase",
        "EU": "Entwurfsübung",
        "EX": "Exkursion",
        "FU": "Feldübung",
        "IP": "Interdisziplinäre Projekte",
        "KO": "Konversatorium",
        "KU": "Konstruktionsübung",
        "KV": "Konversatorium",
        "LU": "Laborübung",
        "MU": "Messübung",
        "PA": "Projektarbeit",
        "PN": "Präsentation",
        "PR": "Projekt",
        "PS": "Proseminar",
        "PU": "Praktische Übung",
        "PV": "Privatissimum",
        "RE": "Repetitorium",
        "RU": "Rechenübung",
        "RV": "Ringvorlesung",
        "SE": "Seminar",
        "SP": "Seminar mit Praktikum",
        "SV": "Spezialvorlesung",
        "UX": "Übung und Exkursion",
        "VD": "Vorlesung mit Demonstrationen",
        "VL": "Vorlesung mit Laborübung",
        "VR": "Vorlesung und Rechenübung",
        "VX": "Vorlesung und Exkursion",
        "ZU": "Zeichenübung",
    }

    def __init__(self, properites, ical_event: Event):
        self.properties = properites
        self.ical_event = ical_event

    def set_description(self, format):
        applied_format = self._apply_format(format)
        altrep_content = self._create_description_altrep_content(applied_format)
        del self.ical_event["description"]
        self.ical_event.add("description", applied_format, { "altrep" : altrep_content })

    def set_summary(self, format):
        self.ical_event["summary"] = self._apply_format(format)

    def set_location(self, format):
        self.ical_event["location"] = self._apply_format(format)

    def _create_description_altrep_content(self, format):
        uri_encoded = urllib.parse.quote(format)
        return f'data:text/html,{uri_encoded}'

    def _apply_format(self, format):
        rtemplate = Environment(loader=BaseLoader()).from_string(format)
        return rtemplate.render(**self.properties)

    @staticmethod
    def is_lva(ical_event: Event) -> bool:
        pattern = re.compile("^(.{3}\..{3}) (.{2}) (.*)$")
        return "summary" in ical_event and pattern.match(ical_event["summary"])

    @staticmethod
    def is_lva_str(event_summary: str) -> bool:
        pattern = re.compile("^(.{3}\..{3}) (.{2}) (.*)$")
        return pattern.match(event_summary) is not None

    @classmethod
    def lva_from_ical_event(cls, ical_event):
        pattern = re.compile("^(.{3}\..{3}) (.{2}) (.*)$")

        # if not LVA
        if not cls.is_lva(ical_event):
            return None

        # if LVA
        match = pattern.match(ical_event["summary"])
        lva_id, lva_type_short, lva_name = match.groups()
        lva_type_long = cls.LVA_TYPE_MAP[lva_type_short]

        start_date, start_time = ical_event["dtstart"].dt.strftime("%d.%m.%Y %H:%M").split(" ")
        end_date, end_time = ical_event["dtend"].dt.strftime("%d.%m.%Y %H:%M").split(" ")

        tiss_course_detail_link = f'https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr={lva_id.replace(".", "")}'
        tiss_education_detail_link = f'https://tiss.tuwien.ac.at/course/educationDetails.xhtml?courseNr={lva_id.replace(".", "")}'
        tiss_cal_desc = ical_event["description"]

        categorie = str(ical_event["categories"].cats[0])

        room_data = get_room_data(ical_event.get("location", None))
        if room_data is not None:
            room_name = room_data[0]
            room_tiss = room_data[1]
            room_tuw_map = room_data[2]
            room_building_address = room_data[3]
        elif "location" in ical_event:
            room_name = ical_event["location"]
            room_tiss = ical_event["location"]
            room_tuw_map = ical_event["location"]
            room_building_address = ical_event["location"]
        else:
            room_name = None
            room_tiss = None
            room_tuw_map = None
            room_building_address = None

        props = {
            "LvaName": lva_name,
            "LvaTypeShort": lva_type_short,
            "LvaTypeLong": lva_type_long,
            "LvaId": lva_id,
            "StartDate": start_date,
            "StartTime": start_time,
            "EndDate": end_date,
            "EndTime": end_time,
            "TissCourseDetailLink": tiss_course_detail_link,
            "TissEducationDetailLink": tiss_education_detail_link,
            "TissCalDesc": tiss_cal_desc,
            "RoomName": room_name,
            "RoomTiss": room_tiss,
            "RoomTuwMap": room_tuw_map,
            "RoomBuildingAddress": room_building_address,
            "Categorie": categorie,
        }

        return cls(props, ical_event)
