
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.models.transfer import Transfer
from app.models.transaction import Transaction


def transfer_money(
    db: Session,
    sender_wallet_id: int,
    receiver_wallet_id: int,
    amount: Decimal,
    idempotency_key: str,
) -> Transfer:
    if (
        not amount.is_finite()
        or amount <= 0
        or amount.as_tuple().exponent < -2
    ):
        raise HTTPException(status_code=400, detail="Invalid transfer amount")

    if sender_wallet_id == receiver_wallet_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same wallet")

    if not idempotency_key or len(idempotency_key) > 100:
        raise HTTPException(status_code=400, detail="Invalid idempotency key")

    try:
        existing = (
            db.query(Transfer)
            .filter(Transfer.idempotency_key == idempotency_key)
            .first()
        )

        if existing:
            if (
                existing.sender_wallet_id != sender_wallet_id
                or existing.receiver_wallet_id != receiver_wallet_id
                or existing.amount != amount
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Idempotency key already used for a different transfer",
                )
            return existing

        wallet_ids = sorted([sender_wallet_id, receiver_wallet_id])

        wallets = (
            db.query(Wallet)
            .filter(Wallet.id.in_(wallet_ids))
            .order_by(Wallet.id)
            .with_for_update()
            .all()
        )
        wallet_map = {wallet.id: wallet for wallet in wallets}

        sender = wallet_map.get(sender_wallet_id)
        receiver = wallet_map.get(receiver_wallet_id)

        if sender is None or receiver is None:
            raise HTTPException(status_code=404, detail="Wallet not found")

        if sender.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")

        sender.balance -= amount
        receiver.balance += amount

        transfer = Transfer(
            sender_wallet_id=sender.id,
            receiver_wallet_id=receiver.id,
            amount=amount,
            status="COMPLETED",
            reference=f"TRF-{uuid4().hex}",
            idempotency_key=idempotency_key,
        )
        db.add(transfer)
        db.flush()

        db.add_all([
            Transaction(
                wallet_id=sender.id,
                transaction_type="TRANSFER_OUT",
                amount=amount,
                status="COMPLETED",
                reference=f"{transfer.reference}-OUT",
            ),
            Transaction(
                wallet_id=receiver.id,
                transaction_type="TRANSFER_IN",
                amount=amount,
                status="COMPLETED",
                reference=f"{transfer.reference}-IN",
            ),
        ])

        db.commit()
        db.refresh(transfer)
        return transfer

    except Exception:
        db.rollback()
        raise
