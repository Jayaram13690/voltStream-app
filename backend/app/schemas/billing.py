from datetime import datetime

from pydantic import BaseModel


class BillingTransactionRead(BaseModel):
    id: int
    label: str
    amount: float
    paid_at: datetime

    model_config = {"from_attributes": True}


class BillingSummary(BaseModel):
    current_bill: float
    predicted_bill: float
    budget_limit: float
    transactions: list[BillingTransactionRead]
