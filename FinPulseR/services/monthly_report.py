import os

from FinPulseR.jwt_auth import enforce_token_authentication
from FinPulseR.database import get_db
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from random import random
from dotenv import load_dotenv
from FinPulseR.services.aws_service import S3Uploader
from FinPulseR.services.common_functions import get_current_user, get_monthly_report_data, get_expense_summary
from FinPulseR.services.report_generator import ReportGenerator

load_dotenv()

@enforce_token_authentication
async def get_monthly_report(request: Request, db: Session = Depends(get_db), email: str = None):
    user_id = get_current_user(email, db)
    monthly_data = get_monthly_report_data(user_id=user_id, db=db)

    generator = ReportGenerator()

    categories = [item[0] for item in monthly_data]
    money_spent = [item[1] for item in monthly_data]
    budget = [item[2] for item in monthly_data]
    this_month_expenses, avg_monthly_expense = get_expense_summary(db, user_id)

    # Create graphs
    graph1 = generator.create_bar_graph(categories, money_spent, budget, "Money Spent vs Budget by Category")
    graph2 = generator.create_bullet_chart(this_month_expenses, avg_monthly_expense,
                                           f"This Month\'s Expenses vs Average Monthly Expenses")

    # Generate PDF
    file_buffer = generator.generate_pdf(
        "report.pdf",
        "FINPULSE EXPENSE REPORT",
        [
            ("Money Spent vs Budget by Category", graph1),
            ("This Month\'s Expenses vs Average Monthly Expenses", graph2)
        ],
        "Below are some details of your this month's Expenses."
    )

    s3_uploader = S3Uploader(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
        bucket_name=os.getenv("AWS_BUCKET")
    )
    file_name = f"{email.split('@')[0]}_{int(random()*1000000)}.pdf"
    data = s3_uploader.upload_bytesio(file_buffer, file_name, "finpulse/userdata/")

    return {"success": True, "data": data}