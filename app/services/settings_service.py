from app.models.user_settings_model import UserSettings
from app.repositories.user_settings_repository import UserSettingsRepository


class SettingsService:

    @staticmethod
    async def get_settings(user_id: str):
        return await UserSettingsRepository.get_settings(user_id)

    @staticmethod
    async def update_settings(settings: UserSettings):
        return await UserSettingsRepository.update_settings(settings)
