from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StorePriceRecord(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    product_id: str
    store_name: str
    price: float
    url: str
    last_checked: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
