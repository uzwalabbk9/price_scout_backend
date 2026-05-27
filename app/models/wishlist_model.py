from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from bson import ObjectId


class WishlistItem(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = "default_user"
    product_id: str
    product_title: str
    product_description: Optional[str] = None
    product_image: Optional[str] = None
    store_name: Optional[str] = None
    current_price: float = 0.0
    product_url: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


class WishlistItemUpdate(BaseModel):
    product_title: Optional[str] = None
    product_description: Optional[str] = None
    product_image: Optional[str] = None
    store_name: Optional[str] = None
    current_price: Optional[float] = None
    product_url: Optional[str] = None
