
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransferResponse(BaseModel):
    id: int
    sender_wallet_id: int
    receiver_wallet_id: int
    amount: Decimal
    status: str
    reference: str

    model_config = ConfigDict(from_attributes=True)
