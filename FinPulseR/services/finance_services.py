import datetime

from FinPulseR.jwt_auth import enforce_token_authentication
from FinPulseR.models import Expense, Category
from FinPulseR.database import get_db
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from FinPulseR.services.common_functions import get_current_user, verify_category, verify_monthly_limit


def create_new_expense():
    return {"data": True}


async def get_expenses(db: Session = Depends(get_db)):
    expenses = db.query(Expense).all()
    return expenses


@enforce_token_authentication
async def add_expense(request: Request, db: Session = Depends(get_db), data: dict = None, email: str = None):
    user_id = get_current_user(email, db)

    is_verified = verify_category(user_id=user_id, data=data, db=db)
    if is_verified.get("success") is False:
        return is_verified

    new_expense_obj = Expense()
    new_expense_obj.user_id = user_id
    new_expense_obj.amount = data.get("amount")
    new_expense_obj.category = data.get("category")
    new_expense_obj.description = data.get("description")
    new_expense_obj.date = datetime.datetime.now()
    db.add(new_expense_obj)
    db.commit()
    is_limit_reached = verify_monthly_limit(user_id=user_id, data=data, db=db)

    return {"success": True, "message": f"Amount {data.get('amount')} is added to category {data.get('category')}",
            "monthly_limit_status": is_limit_reached.get("message")}
