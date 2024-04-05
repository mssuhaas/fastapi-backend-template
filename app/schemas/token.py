"""
This module contains the schema for tokens.
"""

import datetime
from pydantic import BaseModel


class TokenCreate(BaseModel):
    """
    Schema for creating a token.
    """

    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime


class TokenSchema(BaseModel):
    """
    Schema for a token.
    """

    access_token: str
    refresh_token: str = None


class TokenRefresh(BaseModel):
    """
    Schema for a refresh token.
    """

    refresh_token: str
