from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from models.ResponseBase import ResponseBase


class _TissCalEventModel(BaseModel):
    name: str
    will_prettify: bool = False
    will_remove: bool = False
    is_lva: bool = False
    summaryFormat: str = None
    locationFormat: str = None
    descriptionFormat: str = None


class _TissCalDefaultTemplateModel(BaseModel):
    defaultSummaryFormat: str = "{{LvaTypeShort}} {{LvaName}}"
    defaultLocationFormat: str = "{{RoomBuildingAddress}}"
    defaultDescriptionFormat: str = """<b>{{LvaName}}</b>
Typ: <b>{{LvaTypeShort}}</b> ({{LvaTypeLong}})
Details: <b><a href="{{TissDetail}}">TISS</a></b>
Raum: <b>{{RoomName}}</b>, <a href="{{RoomTiss}}">TISS</a>, <a href="{{RoomTuwMap}}">TU-Wien Maps</a>
Full-Name: {{LvaId}} {{LvaTypeShort}} {{LvaName}}
<br>
Tiss Description:
{{TissCalDesc}}"""


class _TissCalBase(BaseModel):
    url: str
    name: str
    token: str

    all_events: list[_TissCalEventModel]
    default_template: _TissCalDefaultTemplateModel = _TissCalDefaultTemplateModel()


class TissCalDBCreate(_TissCalBase):
    owner: str


class TissCalDB(_TissCalBase):
    id: ObjectId = Field(..., alias="_id")
    owner: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class TissCalResponse(_TissCalBase, ResponseBase):
    pass


class TissCalCreateRequest(BaseModel):
    url: str
    name: str


class TissCalCreateResponse(TissCalResponse):
    pass


class TissCalDataResponse(TissCalResponse):
    pass


class TissCalChangeRequest(_TissCalBase):
    pass


class TissCalChangeResponse(TissCalResponse):
    pass


class TissCalUpdateResponse(TissCalResponse):
    pass


class TissCalListResponse(ResponseBase):
    calendars: list[_TissCalBase] = []


class TissCalSuccessDeleteResponse(ResponseBase):
    message: str = "Calendar deleted successfully :)"
