from fastapi import APIRouter
from FinPulseR.services.finance_services import create_new_expense, get_expense, add_expense


router = APIRouter()
router.add_api_route('/', create_new_expense, methods=["GET"])
router.add_api_route('/expenses', get_expense, methods=["GET"])
router.add_api_route('/expenses', add_expense, methods=["POST"])
