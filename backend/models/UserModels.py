from bson import ObjectId
from pydantic import BaseModel, Field

from models.ResponseBase import ResponseBase


class __UserBase(BaseModel):
    username: str
    password: str


class UserDB(__UserBase):
    uid: ObjectId = Field(..., alias="_id")
    username: str
    usernameLower: str
    password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UserResponse(ResponseBase):
    # TODO: Find a way to make this work ()
    username: str


# class UserResponse(__UserBase, ResponseBase):
#     class Config:
#         fields = { 'password': { 'exclude': True }}


class UserLoginRequest(__UserBase):
    pass


class UserLoginResponse(UserResponse):
    pass


class UserLogoutResponse(ResponseBase):
    message: str = Field(default="Successfully logged out")


class UserCreateRequest(__UserBase):
    pass


class UserCreateResponse(ResponseBase):
    pass


class UserDeleteRequest(__UserBase):
    pass


class UserDeleteResponse(ResponseBase):
    message: str = Field(default="Successfully deleted user")
