from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class QRCodeRequest(BaseModel):
    url: HttpUrl
    format: str = "png"


class QRCodeResponse(BaseModel):
    id: UUID
    url: str
    image_url: str
    format: str
    created_at: datetime
