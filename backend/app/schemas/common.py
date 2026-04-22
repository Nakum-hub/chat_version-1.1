from datetime import datetime

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(APIModel):
    message: str


class PageMeta(APIModel):
    limit: int
    offset: int
    total: int


class TimestampedModel(APIModel):
    id: str
    created_at: datetime
    updated_at: datetime