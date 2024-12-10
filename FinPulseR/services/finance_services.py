import datetime

from FinPulseR.jwt_auth import enforce_token_authentication
from FinPulseR.models import Expense, Category
from FinPulseR.database import get_db
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from FinPulseR.services.common_functions import get_current_user, verify_category, verify_monthly_limit, get_month_data
from FinPulseR.services.email_service import EmailBody, send_email

def create_new_expense():
    return {"data": True}


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
    email_body = EmailBody(
        to=email,
        subject="Alert from FinPulse",
        message=is_limit_reached.get("message")
    )
    await send_email(email_body)

    return {"success": True, "message": f"Amount {data.get('amount')} is added to category {data.get('category')}",
            "monthly_limit_status": is_limit_reached.get("message")}


@enforce_token_authentication
async def get_expense(request: Request, db: Session = Depends(get_db), email: str = None):
    user_id = get_current_user(email, db)
    monthly_data = get_month_data(user_id=user_id, db=db)
    formatted_data = [
        {"category": category, "spent": spent, "budget": budget}
        for category, spent, budget in monthly_data
    ]
    return {"success": True, "data": formatted_data}
