from pydantic import BaseModel, Field
from typing import Optional


class UserSettings(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    currency: str = "GBP"
    notifications_enabled: bool = True

    model_config = {"populate_by_name": True}
