
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.wallet import Wallet


def deposit_money(
    db: Session,
    wallet_id: int,
    amount: Decimal,
) -> Wallet:
    if (
        not amount.is_finite()
        or amount <= 0
        or amount.as_tuple().exponent < -2
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid deposit amount",
        )

    try:
        wallet = (
            db.query(Wallet)
            .filter(Wallet.id == wallet_id)
            .with_for_update()
            .first()
        )

        if wallet is None:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found",
            )

        wallet.balance += amount

        transaction = Transaction(
            wallet_id=wallet.id,
            transaction_type="DEPOSIT",
            amount=amount,
            status="COMPLETED",
            reference=f"DEP-{uuid4().hex}",
        )

        db.add(transaction)
        db.commit()
        db.refresh(wallet)

        return wallet

    except Exception:
        db.rollback()
        raise
