from FinPulseR.models import User
from FinPulseR.database import get_db
from fastapi import Depends, requests
from fastapi import Request
from sqlalchemy.orm import Session
from FinPulseR.utils import Hasher, JWT_Token
from FinPulseR.jwt_auth import enforce_token_authentication


def create_new_expense():
    return {"data": True}


@enforce_token_authentication
async def get_users(request: Request, db: Session = Depends(get_db)):
    expenses = db.query(User).all()
    return expenses


async def sign_in(user_data: dict, db: Session = Depends(get_db)):
    email = user_data["email"]
    password = user_data["password"]
    user_obj = db.query(User).filter(User.email == email).first()
    if user_obj is None:
        return {"success": False, "message": "user not found"}
    if Hasher.verify_password(password, user_obj.password) is False:
        return {"success": False, "message": "Incorrect password"}
    return {
        "success": True,
        "Access Token": JWT_Token.create_access_token(email),
        "Refresh Token": JWT_Token.create_refresh_token(email),
        "message": "Login Successful!"
    }


async def sign_up(user_data: dict, db: Session = Depends(get_db)):
    email = user_data["new_email"]
    password = user_data["password"]
    check_existing_user = db.query(User).filter(User.email == email).first()
    if check_existing_user:
        return {"success": False, "message": "email already present"}
    user_obj = User()
    user_obj.email = email
    user_obj.password = Hasher.get_password_hash(password)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return {"success": True, "user": email, "message": "User Created"}
