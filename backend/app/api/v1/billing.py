from fastapi import APIRouter
from datetime import datetime, timedelta

from app.schemas.billing import BillingSummary, BillingTransactionRead

router = APIRouter(prefix="/billing", tags=["billing"])

# Mock billing data
_billing_summary = {
    "current_bill": 128.4,
    "predicted_bill": 156.2,
    "budget_limit": 180.0
}

# Mock transactions
_transactions = [
    {"id": 1, "label": "May payment", "amount": 128.4, "paid_at": datetime.now() - timedelta(days=3)},
    {"id": 2, "label": "April payment", "amount": 119.2, "paid_at": datetime.now() - timedelta(days=33)},
    {"id": 3, "label": "March payment", "amount": 121.0, "paid_at": datetime.now() - timedelta(days=63)},
]


@router.get("/summary", response_model=BillingSummary)
def billing_summary() -> BillingSummary:
    return BillingSummary(
        current_bill=_billing_summary["current_bill"],
        predicted_bill=_billing_summary["predicted_bill"],
        budget_limit=_billing_summary["budget_limit"],
        transactions=[BillingTransactionRead.model_validate(t) for t in _transactions],
    )
