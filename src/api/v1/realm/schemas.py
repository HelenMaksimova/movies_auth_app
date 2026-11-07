from datetime import datetime

from pydantic import BaseModel, ConfigDict

__all__ = ("PublicKeyResponseSchema",)


class PublicKeyResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expires_at: datetime
    public_key: str
