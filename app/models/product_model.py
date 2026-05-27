from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId


class StorePrice(BaseModel):
    store_name: str
    price: float
    currency: str = "GBP"
    delivery_cost: float = 0.0        # ← was required, now has default
    delivery_time: str = ""           # ← was required, now has default
    in_stock: bool = True
    affiliate_link: Optional[str] = None
    url: Optional[str] = None         # ← added for scraper compatibility

    model_config = {"populate_by_name": True}


class ProductCreate(BaseModel):
    title: str
    url: Optional[str] = None         # ← was required, now optional
    description: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None


class Product(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    description: Optional[str] = None
    url: Optional[str] = None         # ← was required, now optional
    image: Optional[str] = None
    category: Optional[str] = None
    store_prices: List[StorePrice] = []
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
