import random
import string
from fastapi import FastAPI, Response, status, Cookie
from fastapi.responses import StreamingResponse
from pymongo import MongoClient
from typing import Dict, Union, List
from pydantic import BaseModel
from io import StringIO
from calFormatter import get_cal_from_url, Lva

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


app = FastAPI()

test_data = {
    'uid': 'associated User',
    'tissCalUrl': "https://tiss.tuwien.ac.at/events/rest/calendar/personal?locale=de&token=6613677f-b201-48b1-a87f-239a163c0b05",
    'unwantedEvents': ['104.263 UE Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik'],
    'prettyEvents': {
        "104.265 VO Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik": {},
        "104.263 UE Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik - P": {},
        "192.134 VU Grundzüge digitaler Systeme": {},
        "185.A91 VU Einführung in die Programmierung 1": {},
        "187.B12 VU Denkweisen der Informatik": {},
        "180.766 VU Orientierung Informatik und Wirtschaftsinformatik": {},
    },
    'defaultSummaryFormat': '{{LvaTypeShort}} {{LvaName}}',
    'defaultLocationFormat': '{{RoomBuildingAddress}}',
    'defaultDescriptionFormat': """<b>{{LvaName}}</b>
Typ: <b>{{LvaTypeShort}}</b> ({{LvaTypeLong}})
Details: <b><a href="{{TissDetail}}">TISS</a></b>
Raum: <b>{{RoomName}}</b>, <a href="{{RoomTiss}}">TISS</a>, <a href="{{RoomTuwMap}}">TU-Wien Maps</a>
Full-Name: {{LvaId}} {{LvaTypeShort}} {{LvaName}}
<br>
Tiss Description:
{{TissCalDesc}}""",
    'calendarToken': 'ZW0awBfTOmpHN7oBmw8jlm5bbWsanT'
}

def generate_calendar(data):
    cal = get_cal_from_url(data['tissCalUrl'])
    
    # Delete unwanted events
    cal.subcomponents = [el for el in cal.subcomponents 
        if el.get('summary', '') not in data['unwantedEvents']]
    
    # Polish known events and leave unknown events untouched
    for event in cal.walk(name='VEVENT'):
        if event['summary'] not in data['prettyEvents']:
            continue

        ev = Lva.lva_from_ical_event(event)
        if ev is None:
            continue

        location_format = data['prettyEvents'][event['summary']].get('locationFormat', data['defaultLocationFormat'])
        ev.set_location(location_format)

        desc_format = data['prettyEvents'][event['summary']].get('descriptionFormat', data['defaultDescriptionFormat'])
        ev.set_description(desc_format)

        # Summary needs to be set last!!!
        summary_format = data['prettyEvents'][event['summary']].get('summaryFormat', data['defaultSummaryFormat'])
        ev.set_summary(summary_format)
    
    return cal.to_ical().decode('utf-8')


def get_cal_data_by_token(token):
    # TODO Client config more human :)
    client = MongoClient("mongodb://root:rootPassword@192.168.0.100/")
    collection = client.get_database('tisscal').get_collection('calendars')
    res = collection.find_one({'calendarToken': token})
    client.close()
    return res


def get_cal_data_by_uid(uid):
    # TODO Client config more human :)
    client = MongoClient("mongodb://root:rootPassword@192.168.0.100/")
    collection = client.get_database('tisscal').get_collection('calendars')
    res = collection.find_one({'uid': uid})
    client.close()
    return res


def generate_token(length):
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for i in range(length))
    return token


class CalModelResponse(BaseModel):
    tissCalUrl: str
    unwantedEvents: List[str]
    prettyEvents: Dict[str, Dict[str, str]]
    defaultSummaryFormat: str
    defaultLocationFormat: str
    defaultDescriptionFormat: str
    calToken: str


class CalModelRequest(BaseModel):
    tissCalUrl: str
    unwantedEvents: List[str]
    prettyEvents: Dict[str, Dict[str, str]]
    defaultSummaryFormat: str
    defaultLocationFormat: str
    defaultDescriptionFormat: str


class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    loggedIn: bool
    message: str

class UserResponse(BaseModel):
    uid: str
    username: str
    usernameLower: str

class UserCreateRequest(BaseModel):
    username: str
    password: str

class UserCreateResponse(BaseModel):
    uid: str
    username: str


@app.post("/tisscal/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(user: LoginRequest):
    
    return {
        "loggedIn": True,
        "message": "you are successfully logged in :)"
    }

@app.post("/tisscal/createUser", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def login(user: UserCreateRequest):
    
    return 


@app.get("/tisscal/{token}", status_code=status.HTTP_200_OK)
async def get_calender(token: str, response: Response):
    cal_data = get_cal_data_by_token(token)
    
    if cal_data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "No Calendar for you (check if you typed the URL correctly) :/"
    
    new_cal = generate_calendar(cal_data)
    new_cal_stream = StringIO(new_cal)
    return StreamingResponse(iter([new_cal_stream.getvalue()]), media_type="text/calendar")


@app.post("/tisscal/", response_model=CalModelResponse, status_code=status.HTTP_200_OK)
async def alter_cal(cal: CalModelRequest, response: Response, uid: Union[str, None] = Cookie(default=None)):
    if uid is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "you need to log in :)"


    # TODO Client config more human :)
    client = MongoClient("mongodb://root:rootPassword@192.168.0.100/")
    collection = client.get_database('tisscal').get_collection('calendars')

    cal_data = get_cal_data_by_uid(uid)
    if cal_data is None:
        cal['uid'] = uid
        cal['calendarToken'] = generate_token(40)
        collection.insert_one(cal)
    else:
        cal['uid'] = uid
        cal['calendarToken'] = cal_data['calendarToken']
        collection.insert_one(cal)
    client.close()
