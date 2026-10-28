from app.routes import auth, wallets, transactions, transfers, profile
from fastapi import FastAPI
from app.routes import transfers
from app.routes import auth, wallets, transactions
from app.routes import profile
app = FastAPI(
    title="Digital Wallet & Transaction Platform",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(wallets.router)
app.include_router(transactions.router)
app.include_router(transfers.router)
app.include_router(profile.router)
@app.get("/")
def root():
    return {"message": "Digital Wallet Platform API is running"}
