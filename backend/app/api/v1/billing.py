from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.billing import Billing, BillingTransaction
from app.schemas.billing import BillingSummary, BillingTransactionRead

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/summary", response_model=BillingSummary)
def billing_summary(db: Session = Depends(get_db)) -> BillingSummary:
    row = db.query(Billing).order_by(Billing.id.desc()).first()
    if row is None:
        return BillingSummary(current_bill=0.0, predicted_bill=0.0, budget_limit=0.0, transactions=[])
    txs = db.query(BillingTransaction).order_by(BillingTransaction.paid_at.desc()).limit(20).all()
    return BillingSummary(
        current_bill=row.current_bill,
        predicted_bill=row.predicted_bill,
        budget_limit=row.budget_limit,
        transactions=[BillingTransactionRead.model_validate(t) for t in txs],
    )
