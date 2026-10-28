
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.transfer import Transfer
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transfer import Transfer
from app.schemas.wallet import WalletTransferRequest
from app.schemas.transfer import TransferResponse
from app.services.transfer_service import transfer_money

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("/", response_model=TransferResponse)
def create_transfer(
    transfer_data: WalletTransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sender_wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if not sender_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your wallet was not found",
        )

    if sender_wallet.id == transfer_data.receiver_wallet_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer money to your own wallet",
        )

    return transfer_money(
        db=db,
        sender_wallet_id=sender_wallet.id,
        receiver_wallet_id=transfer_data.receiver_wallet_id,
        amount=transfer_data.amount,
        idempotency_key=transfer_data.idempotency_key,
    )


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_my_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sender_wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if not sender_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    transfer = (
        db.query(Transfer)
        .filter(
            Transfer.id == transfer_id,
            Transfer.sender_wallet_id == sender_wallet.id,
        )
        .first()
    )

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found",
        )

    return transfer

    transfer = (
        db.query(Transfer)
        .filter(
            Transfer.id == transfer_id,
            (
                (Transfer.sender_wallet_id == sender_wallet.id)
                | (
                    Transfer.receiver_wallet_id
                    == sender_wallet.id
                )
            ),
        )
        .first()
    )

@router.get("/", response_model=list[TransferResponse])
def get_my_transfers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    transfers = (
        db.query(Transfer)
        .filter(
            (Transfer.sender_wallet_id == wallet.id)
            | (Transfer.receiver_wallet_id == wallet.id)
        )
        .order_by(Transfer.id.desc())
        .all()
    )

    return transfers
