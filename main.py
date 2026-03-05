from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="AI Transaction Service")

# ==============================
# CONFIGURATION
# ==============================

INTERNAL_AI_API_KEY = "super-secret-ai-key"

# ==============================
# FAKE DATABASE (In-Memory)
# ==============================

transactions_table = [
    {
        "transaction_id": "TXN001",
        "customer_id": "user_1",
        "customer_name": "John Doe",
        "network": "MTN",
        "amount": 1000,
        "status": "SUCCESS",
        "created_at": datetime.now()
    },
    {
        "transaction_id": "TXN002",
        "customer_id": "user_1",
        "customer_name": "John Born",
        "network": "AIRTEL",
        "amount": 2000,
        "status": "PENDING",
        "created_at": datetime.now()
    },
    {
        "transaction_id": "TXN003",
        "customer_id": "user_2",
        "customer_name": "Sarah K",
        "network": "GLO",
        "amount": 500,
        "status": "FAILED",
        "created_at": datetime.now()
    },
]

# ==============================
# SECURITY DEPENDENCIES
# ==============================

def verify_ai_api_key(x_ai_api_key: str = Header(...)):
    """
    Validates that request is coming from trusted AI agent.
    """
    if x_ai_api_key != INTERNAL_AI_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid AI API Key")
    return True


def get_authenticated_user(x_user_id: str = Header(...)):
    """
    Simulated user authentication.
    In production, this would decode JWT.
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return x_user_id


# ==============================
# RESPONSE MODEL
# ==============================

class TransactionResponse(BaseModel):
    transaction_id: str
    network: str
    amount: float
    status: str
    created_at: datetime


# ==============================
# ENDPOINT
# ==============================

@app.get("/ai/transaction/{transaction_id}", response_model=TransactionResponse)
def get_transaction_details(
    transaction_id: str,
    api_key_valid: bool = Depends(verify_ai_api_key),
    current_user: str = Depends(get_authenticated_user)
):
    """
    AI Agent Endpoint:
    - Requires internal AI API key
    - Requires authenticated user ID
    - Returns transaction ONLY if it belongs to user
    """

    # Scoped lookup
    transaction = next(
        (
            txn for txn in transactions_table
            if txn["transaction_id"] == transaction_id
            and txn["customer_id"] == current_user
        ),
        None
    )

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found or does not belong to user"
        )

    return transaction


# ==============================
# HEALTH CHECK
# ==============================

@app.get("/health")
def health_check():
    return {"status": "AI Transaction Service Running"}