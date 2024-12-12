from FinPulseR.jwt_auth import enforce_token_authentication
from FinPulseR.database import get_db
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from FinPulseR.services.common_functions import get_current_user, get_monthly_report_data


@enforce_token_authentication
async def get_monthly_report(request: Request, db: Session = Depends(get_db), email: str = None):
    user_id = get_current_user(email, db)
    monthly_data = get_monthly_report_data(user_id=user_id, db=db)
    formatted_data = [
        {"category": category, "spent": spent, "budget": budget}
        for category, spent, budget in monthly_data
    ]
    return {"success": True, "data": formatted_data}