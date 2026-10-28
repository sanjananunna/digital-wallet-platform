
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    currency: str

    model_config = ConfigDict(from_attributes=True)


class WalletDeposit(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)


class WalletTransferRequest(BaseModel):
    receiver_wallet_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
idempotency_key: str = Field(min_length=1, max_length=100)