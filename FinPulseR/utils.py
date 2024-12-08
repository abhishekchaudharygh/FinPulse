from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from dotenv import load_dotenv
import jwt

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher():
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


class JWT_Token():
    @staticmethod
    def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRATION_MINUTES", 30)))

        to_encode = {"exp": expires_delta, "email": str(subject)}
        encoded_jwt = jwt.encode(to_encode, os.getenv("JWT_SECRET_KEY"), os.getenv("ALGORITHM"))
        return encoded_jwt

    @staticmethod
    def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 5000)))

        to_encode = {"exp": expires_delta, "email": str(subject)}
        encoded_jwt = jwt.encode(to_encode, os.getenv("JWT_REFRESH_SECRET_KEY"), os.getenv("ALGORITHM"))
        return encoded_jwt
