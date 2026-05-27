from typing import List
from app.models.alerts_model import PriceAlert
from app.repositories.alerts_repository import AlertsRepository


class AlertsService:

    @staticmethod
    async def create_alert(alert: PriceAlert) -> PriceAlert:
        return await AlertsRepository.create_alert(alert)

    @staticmethod
    async def get_user_alerts(user_id: str) -> List[PriceAlert]:
        return await AlertsRepository.get_user_alerts(user_id)

    @staticmethod
    async def deactivate_alert(alert_id: str) -> bool:
        return await AlertsRepository.deactivate_alert(alert_id)
