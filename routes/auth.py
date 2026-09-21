from fastapi import APIRouter, Depends

from schemas.auth import LoginRequest, TokenResponse
from schemas.user import UserResponse
from services import auth_services
from fastapi.security import OAuth2PasswordRequestForm
from db.db import db_dependency
from dependencies.auth import CurrentUser
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    db: db_dependency,
    form_data: OAuth2PasswordRequestForm = Depends()
):

    return auth_services.login_user(
        db=db,
        email=form_data.username,
        password=form_data.password
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user