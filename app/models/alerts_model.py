from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PriceAlert(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    product_id: str
    search_query: str = ""            # ← added: what to search across stores
    target_price: float
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
