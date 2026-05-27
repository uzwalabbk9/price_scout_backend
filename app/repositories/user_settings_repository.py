from typing import Optional
from app.database.connection import get_db
from app.models.user_settings_model import UserSettings


class UserSettingsRepository:

    @staticmethod
    async def get_settings(user_id: str) -> Optional[UserSettings]:
        db = get_db()
        data = await db["user_settings"].find_one({"user_id": user_id})
        if not data:
            return None
        data["_id"] = str(data["_id"])
        return UserSettings(**data)

    @staticmethod
    async def update_settings(settings: UserSettings) -> UserSettings:
        db = get_db()
        await db["user_settings"].update_one(
            {"user_id": settings.user_id},
            {"$set": settings.model_dump(by_alias=True)},
            upsert=True,
        )
        return settings
