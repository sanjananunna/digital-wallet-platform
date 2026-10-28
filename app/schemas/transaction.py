
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class TransactionResponse(BaseModel):
    id: int
    wallet_id: int
    transaction_type: str
    amount: Decimal
    status: str
    reference: str

    model_config = ConfigDict(from_attributes=True)


class TransactionCreate(BaseModel):
    transaction_type: str = Field(pattern="^(DEPOSIT|WITHDRAWAL)$")
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
