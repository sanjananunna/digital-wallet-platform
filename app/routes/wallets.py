
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.schemas.wallet import WalletResponse, WalletDeposit
from app.services.wallet_service import deposit_money

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.post("/", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
def create_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if existing_wallet:
        raise HTTPException(status_code=409, detail="Wallet already exists")

    wallet = Wallet(user_id=current_user.id, balance=Decimal("0.00"))
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


@router.get("/me", response_model=WalletResponse)
def get_my_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return wallet


@router.post("/deposit", response_model=WalletResponse)
def deposit(
    deposit_data: WalletDeposit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    deposit_money(db, wallet.id, deposit_data.amount)
    db.refresh(wallet)
    return wallet


@router.put("/me/currency", response_model=WalletResponse)
def update_wallet_currency(
    currency: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_currencies = {"INR", "USD", "EUR"}

    if currency.upper() not in allowed_currencies:
        raise HTTPException(status_code=400, detail="Unsupported currency")

    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.balance != 0:
        raise HTTPException(
            status_code=400,
            detail="Currency cannot be changed when wallet has a balance",
        )

    has_transactions = (
        db.query(Transaction)
        .filter(Transaction.wallet_id == wallet.id)
        .first()
    )

    if has_transactions:
        raise HTTPException(
            status_code=400,
            detail="Currency cannot be changed after transactions",
        )

    wallet.currency = currency.upper()
    db.commit()
    db.refresh(wallet)
    return wallet


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_empty_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.balance != 0:
        raise HTTPException(
            status_code=400,
            detail="Wallet with a non-zero balance cannot be deleted",
        )

    has_transactions = (
        db.query(Transaction)
        .filter(Transaction.wallet_id == wallet.id)
        .first()
    )

    if has_transactions:
        raise HTTPException(
            status_code=400,
            detail="Wallet with transaction history cannot be deleted",
        )

    db.delete(wallet)
    db.commit()

    return {"message": "Empty wallet deleted successfully"}
