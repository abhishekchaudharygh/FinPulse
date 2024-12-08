from fastapi import APIRouter
from FinPulseR.services.user_auth_services import get_users, sign_in, sign_up

router = APIRouter()
router.add_api_route('/users', get_users, methods=["GET"])
router.add_api_route('/sign-in', sign_in, methods=["POST"])
router.add_api_route('/sign-up', sign_up, methods=["POST"])
