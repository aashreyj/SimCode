# services/user_service.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.repositories import user_repo
from app.auth.security import hash_password, verify_password, is_valid_password
from app.auth.jwt_handler import create_access_token

def signup_user(db: Session, username: str, email: str, password: str, role: str):
    existing_user = user_repo.get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    if not user_repo.is_valid_role(db, role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role}' is not valid"
        )
    
    if not is_valid_password(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and include at least one uppercase letter, "
                    "one lowercase letter, one number, and one special character"
        )

    try:
        hashed_pw = hash_password(password)
        user_repo.create_user(db, username, email, hashed_pw, role)
        return {"message": "User created successfully"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error: Possible duplicate email"
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )


def login_user(db: Session, username: str, password: str):
    user = user_repo.get_user_by_username(db, username)
    # print("in login")
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
