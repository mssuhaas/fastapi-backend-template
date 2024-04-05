"""
This module defines the User model.
"""

from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base
from app.models.user_types import UserType


class User(Base):
    """
    This class defines the User model.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    # is_admin = Column(Boolean, default=False)
    user_type = Column(Integer, default=UserType.CUSTOMER.value)

    def __repr__(self):
        return f"<User {self.username}>"
