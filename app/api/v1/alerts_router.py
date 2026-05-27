from fastapi import APIRouter, HTTPException
from app.models.alerts_model import PriceAlert
from app.services.alerts_service import AlertsService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/", status_code=201)
async def create_alert(alert: PriceAlert):
    """Create a new price alert."""
    created = await AlertsService.create_alert(alert)
    return created


@router.get("/{user_id}")
async def get_user_alerts(user_id: str):
    """Get all alerts for a user."""
    alerts = await AlertsService.get_user_alerts(user_id)
    return alerts


@router.patch("/{alert_id}/deactivate")
async def deactivate_alert(alert_id: str):
    """Deactivate an alert by its id."""
    success = await AlertsService.deactivate_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"deactivated": True}
