from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from app.database.connection import get_db
from app.models.alerts_model import PriceAlert


class AlertsRepository:

    @staticmethod
    async def create_alert(alert: PriceAlert) -> PriceAlert:
        db = get_db()
        data = alert.model_dump(by_alias=True)
        data.pop("_id", None)
        result = await db["alerts"].insert_one(data)
        alert.id = str(result.inserted_id)
        return alert

    @staticmethod
    async def get_active_alerts() -> List[PriceAlert]:
        db = get_db()
        cursor = db["alerts"].find({"active": True})
        docs = await cursor.to_list(length=200)
        alerts = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            alerts.append(PriceAlert(**doc))
        return alerts

    @staticmethod
    async def get_user_alerts(user_id: str) -> List[PriceAlert]:
        db = get_db()
        cursor = db["alerts"].find({"user_id": user_id})
        docs = await cursor.to_list(length=200)
        alerts = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            alerts.append(PriceAlert(**doc))
        return alerts

    @staticmethod
    async def deactivate_alert(alert_id: str) -> bool:
        db = get_db()
        try:
            result = await db["alerts"].update_one(
                {"_id": ObjectId(alert_id)},   # ← was using str, needs ObjectId
                {"$set": {"active": False}},
            )
            return result.modified_count == 1
        except InvalidId:
            return False
