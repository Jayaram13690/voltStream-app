from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.billing import Billing, BillingTransaction
from app.models.device import Device


def seed_if_empty(db: Session) -> None:
    if db.query(Device).first() is None:
        devices = [
            Device(name="Heat pump", status="on", power_usage=2.1),
            Device(name="EV charger", status="off", power_usage=0.0),
            Device(name="Kitchen", status="on", power_usage=0.8),
            Device(name="HVAC", status="on", power_usage=1.4),
            Device(name="Water heater", status="off", power_usage=0.0),
            Device(name="Solar inverter", status="on", power_usage=0.2),
        ]
        db.add_all(devices)

    if db.query(Billing).first() is None:
        db.add(Billing(current_bill=128.4, predicted_bill=156.2, budget_limit=180.0))

    if db.query(BillingTransaction).first() is None:
        now = datetime.now(UTC)
        txs = [
            BillingTransaction(label="May payment", amount=-128.4, paid_at=now - timedelta(days=3)),
            BillingTransaction(label="April payment", amount=-119.2, paid_at=now - timedelta(days=33)),
            BillingTransaction(label="March payment", amount=-121.0, paid_at=now - timedelta(days=63)),
        ]
        db.add_all(txs)

    db.commit()
