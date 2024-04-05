"""
This module contains the main FastAPI application.
"""

from fastapi import FastAPI
from app.routes.user import router as user_router
from app.models.user import User
from app.database import engine as database, get_session, Base
from app.auth.auth import get_hashed_password
from fastapi.middleware.cors import CORSMiddleware
from app.models.user_types import UserType

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



@app.on_event("startup")
async def startup():
    """
    This function is called when the application starts up.
    It connects to the database and creates a default admin user if it doesn't exist.
    """
    Base.metadata.create_all(bind=database)
    # connect to the database
    try:
        database.connect()
        db = next(get_session())

        # check if admin user exists email or username
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            user = db.query(User).filter(User.email == "admin@localhost").first()
            if not user:
                user = User(
                    username="admin",
                    email="admin@localhost",
                    password=get_hashed_password("admin"),
                    user_type=UserType.ADMIN.value
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                print("Admin user already exists")
        else:
            print("Admin user already exists")

    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e


@app.on_event("shutdown")
async def shutdown():
    """
    This function is called when the application shuts down. It disconnects from the database.
    """
    get_session().close()


# include user_router with prefix /user
app.include_router(user_router, prefix="/user")


# Include get_session as a dependency globally
app.dependency_overrides[get_session] = get_session
