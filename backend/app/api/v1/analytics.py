from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analytics import AnalyticsHistory, AnalyticsPoint

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/history", response_model=AnalyticsHistory)
def history(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
) -> AnalyticsHistory:
    del db  # reserved for future persisted analytics
    if period == "daily":
        points = [
            AnalyticsPoint(label="00:00", consumption=1.2, solar=0.0),
            AnalyticsPoint(label="04:00", consumption=0.9, solar=0.0),
            AnalyticsPoint(label="08:00", consumption=2.4, solar=1.8),
            AnalyticsPoint(label="12:00", consumption=3.1, solar=5.6),
            AnalyticsPoint(label="16:00", consumption=2.8, solar=4.2),
            AnalyticsPoint(label="20:00", consumption=3.6, solar=0.4),
        ]
    elif period == "weekly":
        points = [
            AnalyticsPoint(label="Mon", consumption=18.4, solar=22.1),
            AnalyticsPoint(label="Tue", consumption=17.2, solar=24.0),
            AnalyticsPoint(label="Wed", consumption=19.1, solar=21.3),
            AnalyticsPoint(label="Thu", consumption=16.8, solar=25.4),
            AnalyticsPoint(label="Fri", consumption=20.2, solar=23.0),
            AnalyticsPoint(label="Sat", consumption=15.0, solar=26.8),
            AnalyticsPoint(label="Sun", consumption=14.2, solar=27.5),
        ]
    else:
        points = [
            AnalyticsPoint(label="Jan", consumption=520, solar=610),
            AnalyticsPoint(label="Feb", consumption=498, solar=640),
            AnalyticsPoint(label="Mar", consumption=505, solar=720),
            AnalyticsPoint(label="Apr", consumption=480, solar=780),
            AnalyticsPoint(label="May", consumption=460, solar=800),
        ]
    return AnalyticsHistory(period=period, points=points)
