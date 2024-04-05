"""
This module contains Pydantic models for user-related requests and responses.
"""

from pydantic import BaseModel


class UserCreate(BaseModel):
    """
    Pydantic model for creating a new user.
    """

    username: str
    email: str
    password: str
    user_type: int


class RequestDetails(BaseModel):
    """
    Pydantic model for user login request.
    """

    email: str
    password: str


class ChangePassword(BaseModel):
    """
    Pydantic model for changing user password.
    """

    email: str
    old_password: str
    new_password: str
