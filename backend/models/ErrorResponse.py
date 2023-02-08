from pydantic import Field

from models.ResponseBase import Metadata, ResponseBase


class ErrorResponse(ResponseBase):
    metadata: Metadata = Field(default=Metadata(error=True))
    message: str = Field(default="Some error occurred")
