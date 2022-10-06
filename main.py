from icalendar import Calendar
from functools import cache
from fastapi import FastAPI, Response, status
from fastapi.responses import FileResponse
import csv
import requests
import re

# Caleder URL under which the ics file can be found
TISS_CAL_URL = 'https://tiss.tuwien.ac.at/events/rest/calendar/personal?locale=de&token=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

# Events that will be deleted
UNWANTED_EVENTS = ('104.263 UE Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik')

# Events to prettify (if possible will change to nice description, nice location, etc)
PRETTY_EVENTS = (
    "104.265 VO Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik",
    "104.263 UE Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik - P",
    "192.134 VU Grundzüge digitaler Systeme",
    "185.A91 VU Einführung in die Programmierung 1",
    "187.B12 VU Denkweisen der Informatik",
    "180.766 VU Orientierung Informatik und Wirtschaftsinformatik"
)

TOKEN = "ZW0awBfTOmpHN7oBmw8jlm5bbWsanT"

DEFAULT_DESCRIPTION_FROMAT = """<b>{{LvaName}}</b>
Typ: <b>{{LvaTypeShort}}</b> ({{LvaTypeLong}})
Details: <b><a href="{{TissDetail}}">TISS</a></b>
Raum: <b>{{RoomName}}</b>, <a href="{{RoomTiss}}">TISS</a>, <a href="{{RoomTuwMap}}">TU-Wien Maps</a>
Full-Name: {{LvaId}} {{LvaTypeShort}} {{LvaName}}
<br>
Tiss Description:
{{TissCalDesc}}"""

DEFAULT_LOCATION_FROMAT = "{{RoomBuildingAddress}}"

DEFAULT_SUMMARY_FROMAT = "{{LvaTypeShort}} {{LvaName}}"


# EXISTSING:
# TISS-Details Link                                     TissDetail
# TISS-Calender original Description                    TissCalDesc

# Room Name (Ausgeschriebener Raum Name)                RoomName
# Room TISS-Raumbelegung Link                           RoomTiss
# Room TUW-Maps Link                                    RoomTuwMap
# Room Gebäude Addresse (z.B. "Getreidemarkt 9")        RoomBuildingAddress

# StartDate formated as (dd-MM-YYYY)                    StartDate
# StartTime formated as (hh:mm)                         StartTime
# EndDate formated as (dd-MM-YYYY)                      EndDate
# EndTime formated as (hh:mm)                           EndTime

# LVA Name (z.B. "Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik")    LvaName
# LVA Typ kurz (z.B. "VO", "UE", "VU", ...)                                                     LvaTypeShort
# LVA Typ lang (z.B. "Vorlesung", "Übung", "Vorlesung mit Übung")                               LvaTypeLong
# LVA ID (z.B. "104.265")                                                                       LvaId

# TODO:
# Default Template (inserts the default template)


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
        "TissDetail",
        "TissCalDesc",
        "RoomName",
        "RoomTiss",
        "RoomTuwMap",
        "RoomBuildingAddress",
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

    def __init__(self, properites, ical_event):
        self.properties = properites
        self.ical_event = ical_event

    def set_description(self, format):
        self.ical_event["description"] = self._apply_format(format)

    def set_summary(self, format):
        self.ical_event["summary"] = self._apply_format(format)

    def set_location(self, format):
        self.ical_event["location"] = self._apply_format(format)

    def _apply_format(self, format):
        pattern = re.compile("\{\{([a-zA-Z]+)\}\}")
        res = ""
        lastIndex = 0
        
        for x in pattern.finditer(format):
            if x.groups()[0] not in self.PROPERTIES_TEMPLATE:
                continue
            
            res += format[lastIndex:x.span()[0]]
            res += self.properties[x.groups()[0]]

            lastIndex = x.span()[1]

        return res + format[lastIndex:]


    @classmethod
    def lva_from_ical_event(cls, ical_event):
        pattern = re.compile("^(.{3}\..{3}) (.{2}) (.*)$")
        
        # if not LVA
        if 'summary' not in ical_event or not pattern.match(ical_event["summary"]):
            return None

        # if LVA
        match = pattern.match(ical_event["summary"])
        lva_id, lva_type_short, lva_name = match.groups()
        lva_type_long = cls.LVA_TYPE_MAP[lva_type_short]

        start_date, start_time = ical_event['dtstart'].dt.strftime("%d.%m.%Y %H:%M").split(" ")
        end_date, end_time = ical_event['dtend'].dt.strftime("%d.%m.%Y %H:%M").split(" ")

        tiss_detail = f'https://tiss.tuwien.ac.at/course/event/courseDetails.xhtml?foreignId=2022W-{lva_id.replace(".", "")}'
        tiss_cal_desc = ical_event["description"]

        room_data = get_room_data(ical_event.get('location', None))
        if room_data is not None:
            room_name = room_data[0]
            room_tiss = room_data[1]
            room_tuw_map = room_data[2]
            room_building_address = room_data[3]
        elif 'location' in ical_event:
            room_name = ical_event['location']
            room_tiss = ical_event['location']
            room_tuw_map = ical_event['location']
            room_building_address = ical_event['location']
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
            "TissDetail": tiss_detail,
            "TissCalDesc": tiss_cal_desc,
            "RoomName": room_name,
            "RoomTiss": room_tiss,
            "RoomTuwMap": room_tuw_map,
            "RoomBuildingAddress": room_building_address,
        }

        return cls(props, ical_event)


def get_cal_from_url(url):
    req = requests.get(url)
    if req.status_code == 200:
        return Calendar.from_ical(req.content)


@cache
def read_rooms(file="resources/TU-Room.csv"):
    with open("TU-Rooms.csv", "r", encoding="UTF-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        return [room for room in reader]


def get_room_data(room_name=None):
    if room_name == '': return None

    for room in read_rooms():
        if room_name == room[0]:
            return [
                room[0], # Room Name
                room[8], # Tiss Link
                f'https://tuw-maps.tuwien.ac.at/?q={room[7]}#map', # TU Wien Maps Link
                room[6].split(",")[0], # Real World Location
            ]
    else:
        return None


app = FastAPI()


@app.get("/tisscal/{token}", status_code=status.HTTP_200_OK)
async def get_calender(token: str, response: Response):
    if token == TOKEN:
        cal = get_cal_from_url(TISS_CAL_URL)

        # Delete unwanted events
        cal.subcomponents = [el for el in cal.subcomponents 
            if el.get('summary', '') not in UNWANTED_EVENTS]

        # Polish known events and leave unkown events untouched
        for event in cal.walk(name='VEVENT'):
            ev = Lva.lva_from_ical_event(event)
            if ev is None:
                continue
            
            ev.set_summary(DEFAULT_SUMMARY_FROMAT)
            ev.set_location(DEFAULT_LOCATION_FROMAT)
            ev.set_description(DEFAULT_DESCRIPTION_FROMAT)
        
        with open(TOKEN + ".ics", "wb") as f:
            f.write(cal.to_ical())

        return FileResponse(TOKEN + ".ics", media_type="text/calendar")
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
