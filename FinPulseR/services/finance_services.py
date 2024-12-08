from FinPulseR.models import Expense
from FinPulseR.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session


def create_new_expense():
    return {"data": True}


async def get_expenses(db: Session = Depends(get_db)):
    expenses = db.query(Expense).all()
    return expenses
