from fastapi import APIRouter, HTTPException
from app.models.user_settings_model import UserSettings
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/{user_id}")
async def get_settings(user_id: str):
    """Get settings for a user. Returns defaults if none saved yet."""
    settings = await SettingsService.get_settings(user_id)
    if not settings:
        # Return sensible defaults so the Flutter app never crashes
        return UserSettings(user_id=user_id).model_dump()
    return settings.model_dump()


@router.put("/{user_id}")
async def update_settings(user_id: str, settings: UserSettings):
    """Update (or create) settings for a user."""
    settings.user_id = user_id
    updated = await SettingsService.update_settings(settings)
    return updated.model_dump()
