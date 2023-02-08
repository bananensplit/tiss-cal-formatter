from datetime import datetime

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    timestamp: str = Field(default=datetime.now().isoformat())
    error: bool = Field(default=False)


class ResponseBase(BaseModel):
    metadata: Metadata = Field(default=Metadata())
