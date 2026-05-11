from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import numpy as np

# =========================
# DATABASE CONFIG
# =========================

DATABASE_URL = "mysql+pymysql://admin:shivam123456789@fastapi-db33.ce522geuc540.us-east-1.rds.amazonaws.com:3306/fastapi_db"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# =========================
# TABLE
# =========================

class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100))
    amount = Column(Float)
    category = Column(String(100))
    status = Column(String(50))

# Create table automatically
Base.metadata.create_all(bind=engine)

# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="FastAPI Analytics API"
)

# =========================
# SCHEMAS
# =========================

class TransactionCreate(BaseModel):
    user_id: str
    amount: float
    category: str
    status: str


class PredictRequest(BaseModel):
    amount: float
    category: str
    status: str

# =========================
# DATABASE SESSION
# =========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# =========================
# HOME API
# =========================

@app.get("/")
def home():

    return {
        "message": "FastAPI + MySQL RDS Running"
    }

# =========================
# CREATE RECORD
# =========================

@app.post("/records")
def create_record(
    req: TransactionCreate,
    db: Session = Depends(get_db)
):

    new_record = Transaction(
        user_id=req.user_id,
        amount=req.amount,
        category=req.category,
        status=req.status
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "message": "Record Created Successfully",
        "data": {
            "id": new_record.id,
            "user_id": new_record.user_id,
            "amount": new_record.amount,
            "category": new_record.category,
            "status": new_record.status
        }
    }

# =========================
# GET ALL RECORDS
# =========================

@app.get("/records")
def get_records(
    db: Session = Depends(get_db)
):

    records = db.query(Transaction).all()

    return records

# =========================
# GET SINGLE RECORD
# =========================

@app.get("/records/{id}")
def get_record(
    id: int,
    db: Session = Depends(get_db)
):

    record = db.query(Transaction).filter(
        Transaction.id == id
    ).first()

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Record Not Found"
        )

    return record

# =========================
# UPDATE RECORD
# =========================

@app.put("/records/{id}")
def update_record(
    id: int,
    req: TransactionCreate,
    db: Session = Depends(get_db)
):

    record = db.query(Transaction).filter(
        Transaction.id == id
    ).first()

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Record Not Found"
        )

    record.user_id = req.user_id
    record.amount = req.amount
    record.category = req.category
    record.status = req.status

    db.commit()
    db.refresh(record)

    return {
        "message": "Record Updated Successfully",
        "data": {
            "id": record.id,
            "user_id": record.user_id,
            "amount": record.amount,
            "category": record.category,
            "status": record.status
        }
    }

# =========================
# DELETE RECORD
# =========================

@app.delete("/records/{id}")
def delete_record(
    id: int,
    db: Session = Depends(get_db)
):

    record = db.query(Transaction).filter(
        Transaction.id == id
    ).first()

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Record Not Found"
        )

    db.delete(record)
    db.commit()

    return {
        "message": "Record Deleted Successfully"
    }

# =========================
# ANALYTICS SUMMARY
# =========================

@app.get("/analytics/summary")
def analytics_summary(
    db: Session = Depends(get_db)
):

    records = db.query(Transaction).all()

    if not records:

        return {
            "message": "No Records Found"
        }

    amounts = np.array([record.amount for record in records])

    return {

        "total_transactions": len(amounts),

        "total_amount": float(np.sum(amounts)),

        "average_amount": float(np.mean(amounts)),

        "minimum_amount": float(np.min(amounts)),

        "maximum_amount": float(np.max(amounts))
    }

# =========================
# FRAUD DETECTION
# =========================

@app.get("/analytics/fraud")
def fraud_detection(
    db: Session = Depends(get_db)
):

    records = db.query(Transaction).all()

    fraud_records = []

    for record in records:

        if record.amount > 50000:

            fraud_records.append({

                "id": record.id,
                "user_id": record.user_id,
                "amount": record.amount,
                "category": record.category,
                "status": record.status
            })

    return {

        "fraud_count": len(fraud_records),

        "fraud_transactions": fraud_records
    }

# =========================
# CATEGORY ANALYSIS
# =========================

@app.get("/analytics/category")
def category_analysis(
    db: Session = Depends(get_db)
):

    records = db.query(Transaction).all()

    categories = {}

    for record in records:

        if record.category not in categories:

            categories[record.category] = 0

        categories[record.category] += 1

    return {

        "category_distribution": categories
    }

# =========================
# STATUS ANALYSIS
# =========================

@app.get("/analytics/status")
def status_analysis(
    db: Session = Depends(get_db)
):

    records = db.query(Transaction).all()

    statuses = {}

    for record in records:

        if record.status not in statuses:

            statuses[record.status] = 0

        statuses[record.status] += 1

    return {

        "status_distribution": statuses
    }

# =========================
# HIGH VALUE TRANSACTIONS
# =========================

@app.get("/analytics/high-value")
def high_value_transactions(
    db: Session = Depends(get_db)
):

    records = db.query(Transaction).all()

    high_transactions = []

    for record in records:

        if record.amount > 100000:

            high_transactions.append({

                "id": record.id,
                "user_id": record.user_id,
                "amount": record.amount,
                "category": record.category,
                "status": record.status
            })

    return {

        "high_value_count": len(high_transactions),

        "transactions": high_transactions
    }

# =========================
# PREDICTION API
# =========================

@app.post("/predict")
def predict(data: PredictRequest):

    prediction = "Low Risk"

    # High amount transactions
    if data.amount > 50000:
        prediction = "High Risk"

    # Failed transactions
    if data.status.lower() == "failed":
        prediction = "High Risk"

    # Risky categories
    if data.category.lower() in ["luxury", "investment", "electronics"]:
        prediction = "High Risk"

    return {

        "input": {
            "amount": data.amount,
            "category": data.category,
            "status": data.status
        },

        "prediction": prediction
    }
