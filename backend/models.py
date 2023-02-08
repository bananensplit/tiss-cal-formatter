from datetime import datetime
from pydantic import BaseModel, Field


class Metadata(BaseModel):
    timestamp: str = Field(default=datetime.now().isoformat())
    error: bool = Field(default=False)


class ResponseBase(BaseModel):
    metadata: Metadata


class ErrorResponse(ResponseBase):
    metadata: Metadata = Field(default=Metadata(error=True))
    message: str = Field(default="Some error occurred")


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(ResponseBase):
    username: str


class UserLogoutResponse(ResponseBase):
    message: str = Field(default="Successfully logged out")
