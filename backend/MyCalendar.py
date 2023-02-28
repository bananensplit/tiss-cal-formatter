import hashlib
import requests
from icalendar.cal import Calendar, Event

from Lva import Lva


class MyCalendar:
    def __init__(self, url: str, cal: Calendar):
        self.url = url
        self.cal = cal

    @classmethod
    def get_cal_from_url(cls, url: str):
        try:
            req = requests.get(url, timeout=5)
            if req.status_code == 200:
                cal = Calendar.from_ical(req.content)
                return cls(url, cal)
        except Exception as e:
            return None
        return None

    def get_all_events(self) -> list[Event]:
        return [event for event in self.cal.subcomponents if event.name == "VEVENT"]

    def get_events_by_name(self, name: str) -> list[Event]:
        return [event for event in self.cal.subcomponents if event.name == "VEVENT" and event.get("summary", "") == name]

    def get_distinct_events(self) -> list[str]:
        return list(set([event.get("summary") for event in self.cal.subcomponents if event.name == "VEVENT"]))

    def delete_events_by_name(self, name: str):
        for event in self.cal.subcomponents[:]:
            if event.name != "VEVENT":
                continue

            if event.get("summary", "") == name:
                self.cal.subcomponents.remove(event)

    def prettify_events_by_name(self, name, location_template, description_template, summary_template):
        # Format Properties:
        # TISS-Details Link (/courseDetails)                    TissCourseDetailLink
        # TISS-Details Link (/eductaionDetails)                 TissEductionDetailLink
        # TISS-Calender original Description                    TissCalDesc

        # Category of the Event ("EXAM"|"COURSE"|"GROUP")       Category

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

        events = self.get_events_by_name(name)
        for event in events:
            lva = Lva.lva_from_ical_event(event)

            location_format = location_template
            lva.set_location(location_format)

            desc_format = description_template
            lva.set_description(desc_format)

            # Summary needs to be set last!!!
            summary_format = summary_template
            lva.set_summary(summary_format)

    def update_event_uids(self):
        for event in self.get_all_events():
            nice = (
                str(event.get("SUMMARY", ""))
                + str(event.get("DESCRIPTION", ""))
                + str(event.get("DTSTART", "").dt.strftime("%d%m%Y %H%M"))
                + str(event.get("DTEND", "").dt.strftime("%d%m%Y %H%M"))
                + str(event.get("LOCATION", ""))
            )
            hash = hashlib.sha1(nice.encode()).hexdigest()
            event["UID"] = hash

    def to_ical(self):
        return self.cal.to_ical().decode("utf-8")
