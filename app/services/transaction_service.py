
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.transaction import Transaction
from app.models.wallet import Wallet


def get_wallet_transactions(db: Session, wallet_id: int):
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()

    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return (
        db.query(Transaction)
        .filter(Transaction.wallet_id == wallet_id)
        .order_by(Transaction.id.desc())
        .all()
    )


def get_transaction_by_id(db: Session, transaction_id: int):
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction
