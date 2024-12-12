from fastapi import APIRouter
from FinPulseR.services.monthly_report import get_monthly_report

router = APIRouter()
router.add_api_route('/monthly_report', get_monthly_report, methods=["GET"])