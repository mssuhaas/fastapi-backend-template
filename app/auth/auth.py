"""
This module contains functions related to authentication, such as creating and verifying passwords,
creating access and refresh tokens, and checking if a token is valid.
"""

from datetime import datetime, timedelta
from typing import Union, Any
from functools import wraps
from passlib.context import CryptContext
from jose import jwt, JWTError
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException
from app.models.token_table import TokenTable
from app.models.user import User
from app.models.user_types import UserType
from app.config.settings import (
    JWT_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """Return the hashed password"""
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """Verify the password"""
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """Create an access token"""
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta

    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """Create a refresh token"""
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def decode_jwt(jwtoken: str) -> dict:
    """
    Decode and verify the JWT token.

    Args:
    - jwtoken (str): JWT token to decode.

    Returns:
    - dict: Decoded payload if the token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None


# decode refresh token
def decode_refresh_jwt(jwtoken: str) -> dict:
    """
    Decode and verify the JWT token.

    Args:
    - jwtoken (str): JWT token to decode.

    Returns:
    - dict: Decoded payload if the token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(jwtoken, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None


def get_user(jwtoken: str, db: Any) -> Any:
    """
    Get the user from the database.

    Args:
    - jwtoken (str): JWT token to decode.
    - db (Any): Database session.

    Returns:
    - Any: User if the token is valid, None otherwise.
    """
    payload = decode_jwt(jwtoken)
    print(payload)
    if payload is not None:
        user_id = payload.get("sub")
        print(user_id)
        if user_id is not None:
            user = db.query(User).filter(User.id == user_id).first()
            return user
    return None


def token_required(func):
    """Decorator to check if token is valid"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("_request")
        if not request:
            raise HTTPException(status_code=403, detail="Invalid request")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=403, detail="You are not authorized to access this resource"
            )

        scheme, _, token = authorization.partition(" ")

        if scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Invalid authorization scheme")

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
        except JWTError as exc:
            raise HTTPException(
                status_code=403, detail="Invalid token or expired token"
            ) from exc

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=403, detail="Invalid token or expired token"
            )

        data = (
            kwargs["session"]
            .query(TokenTable)
            .filter_by(user_id=user_id, access_token=token, status=True)
            .first()
        )

        if not data:
            raise HTTPException(status_code=403, detail="Token blocked")

        print("Reached end")

        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    """Decorator to check if user is admin"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        request = kwargs.get("_request")
        authorization: str = request.headers.get("Authorization")
        _, _, token = authorization.partition(" ")
        user = get_user(token, kwargs["session"])

        if user.user_type != UserType.ADMIN.value:
            raise HTTPException(
                status_code=403, detail="You are not authorized to access this resource"
            )

        return func(*args, **kwargs)

    return wrapper
