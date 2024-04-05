"""This module defines the TokenTable class."""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base


class TokenTable(Base):
    """This class represents the token table in the database."""

    __tablename__ = "token"
    user_id = Column(Integer)
    access_token = Column(String(450), primary_key=True)
    refresh_token = Column(String(450), nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, access_token, refresh_token, status):
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.status = status

    def __repr__(self):
        return f"<TokenTable(user_id={self.user_id}, access_token={self.access_token}, \
    refresh_token={self.refresh_token}, status={self.status})>"
