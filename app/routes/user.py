"""
This module defines the user routes for the FastAPI application.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, RequestDetails, ChangePassword
from app.schemas.token import TokenSchema, TokenRefresh
from app.models.user import User
from app.models.token_table import TokenTable
from app.database import get_session
from app.auth.auth import (
    decode_refresh_jwt,
    create_access_token,
    create_refresh_token,
    verify_password,
    get_hashed_password,
    token_required,
    admin_required,
)

router = APIRouter()


@router.post("/create-user")
@token_required
@admin_required
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    Registers a new user.

    Args:
        user (UserCreate): The user details.
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Raises:
        HTTPException: If the email is already registered.

    Returns:
        dict: A dictionary containing a success message.
    """
    existing_user = session.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password = get_hashed_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=encrypted_password,
        user_type=user.user_type,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "user created successfully"}


@router.post("/login", response_model=TokenSchema)
def login(request: RequestDetails, db: Session = Depends(get_session)):
    """
    Authenticates a user and returns access and refresh tokens.

    Args:
        request (requestdetails): The request containing the user's email and password.
        db (Session, optional): The database session. Defaults to Depends(get_session()).

    Raises:
        HTTPException: If the email or password is incorrect.

    Returns:
        dict: A dictionary containing the access and refresh tokens.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email"
        )
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = TokenTable(
        user_id=user.id, access_token=access, refresh_token=refresh, status=True
    )
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }


@router.post("/token/refresh", response_model=TokenSchema)
def refresh_token(token: TokenRefresh, db: Session = Depends(get_session)):
    """
    Refreshes an access token using a refresh token.

    Args:
        token (TokenRefresh): The refresh token.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the refresh token is invalid.

    Returns:
        dict: A dictionary containing the new access token.
    """
    payload = decode_refresh_jwt(token.refresh_token)
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid refresh token.")

    access_token = create_access_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/getusers")
@token_required
def getusers(_request: Request, session: Session = Depends(get_session)):
    """
    Returns a list of all users.

    Args:
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Returns:
        list: A list of all users.
    """
    user = session.query(User).all()
    return user


@router.get("/am-i-admin")
@token_required
@admin_required
def am_i_admin(_request: Request, session: Session = Depends(get_session)):
    """
    Checks if the user is an admin.

    Args:
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    return True


@router.post("/change-password")
def change_password(request: ChangePassword, db: Session = Depends(get_session)):
    """
    Changes the password of the user with the given email address.

    Args:
        request (changepassword): The request containing the old and new passwords.
        db (Session, optional): The database session. Defaults to Depends(get_session()).

    Raises:
        HTTPException: If the user is not found or the old password is incorrect.

    Returns:
        dict: A dictionary containing a success message.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
        )

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()

    return {"message": "Password changed successfully"}
