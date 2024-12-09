import jwt
from fastapi import HTTPException, Request
from functools import wraps
from typing import Callable
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TokenValidationError(Exception):
    """Custom exception for token validation errors."""
    pass


def decode_and_validate_token(token: str) -> str:
    """
    Decodes and validates a JWT token.
    Args:
        token (str): The JWT token to validate.
    Returns:
        str: The email address from the token payload.
    Raises:
        HTTPException: If the token is invalid or expired.
    """
    secret_key = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    algorithm = os.getenv("ALGORITHM", "HS256")

    try:
        decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
        return decoded.get("email")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def enforce_token_authentication(func: Callable):
    """
    Decorator to enforce token-based authentication on a route.
    Args:
        func (Callable): The function to be decorated.
    Returns:
        Callable: The wrapped function.
    """

    @wraps(func)
    async def wrapped_function(*args, **kwargs):
        # Extract the request object from kwargs or as a dependency.
        request: Request = kwargs.get("request")
        if not request:
            raise ValueError("Request object is required")

        # Extract the Authorization header.
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        # Extract and validate the JWT token.
        token = auth_header.split(" ")[1]
        email = decode_and_validate_token(token)
        kwargs["email"] = email   # Incase want user email
        # request.state.email = email  # Attach email to the request state
        return await func(*args, **kwargs)

    return wrapped_function
