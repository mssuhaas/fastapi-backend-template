"""
This module defines the User Types model.
"""

from enum import Enum


class UserType(Enum):
    """
    This class defines the user types.
    """
    ADMIN = 1
    VENDOR = 2
    CUSTOMER = 3