from app.models.user_schema import UserIn
from app.service import user_service
from db import get_db
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/signup")
def signup(user: UserIn, db: Session = Depends(get_db)):
    return user_service.signup_user(
        db=db,
        username=user.username,
        email=user.email,
        password=user.password,
        role=user.role_of_user
    )

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return user_service.login_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
