from fastapi import APIRouter, Query

from app.schemas.analytics import AnalyticsHistory, AnalyticsPoint

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/history", response_model=AnalyticsHistory)
def history(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
) -> AnalyticsHistory:
    if period == "daily":
        points = [
            AnalyticsPoint(label="00:00", consumption=1.2, solar=0.0),
            AnalyticsPoint(label="04:00", consumption=0.9, solar=0.0),
            AnalyticsPoint(label="08:00", consumption=2.4, solar=1.8),
            AnalyticsPoint(label="12:00", consumption=9.1, solar=5.6),
            AnalyticsPoint(label="16:00", consumption=8.8, solar=4.2),
            AnalyticsPoint(label="20:00", consumption=3.6, solar=0.4),
        ]
    elif period == "weekly":
        points = [
            AnalyticsPoint(label="Mon", consumption=23.4, solar=22.1),
            AnalyticsPoint(label="Tue", consumption=23.3, solar=24.0),
            AnalyticsPoint(label="Wed", consumption=24.1, solar=21.3),
            AnalyticsPoint(label="Thu", consumption=28.8, solar=25.4),
            AnalyticsPoint(label="Fri", consumption=23.2, solar=23.0),
            AnalyticsPoint(label="Sat", consumption=26.9, solar=26.8),
            AnalyticsPoint(label="Sun", consumption=28.2, solar=27.5),
        ]
    else:
        points = [
            AnalyticsPoint(label="Jan", consumption=610, solar=520),
            AnalyticsPoint(label="Feb", consumption=698, solar=440),
            AnalyticsPoint(label="Mar", consumption=805, solar=720),
            AnalyticsPoint(label="Apr", consumption=790, solar=780),
            AnalyticsPoint(label="May", consumption=801, solar=800),
        ]
    return AnalyticsHistory(period=period, points=points)
