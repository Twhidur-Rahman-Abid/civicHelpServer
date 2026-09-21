from fastapi import APIRouter, Depends, status, UploadFile, File


from db.db import db_dependency
from schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    PasswordReset,
)
from services import user_services

router = APIRouter(prefix="/users", tags=["Users"])




@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(user_in: UserCreate, db: db_dependency):
    return user_services.register_user(db, user_in)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile by ID",
)
def get_user(user_id: int, db: db_dependency):
    return user_services.get_user_by_id(db, user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile details",
)
def update_profile(
    user_id: int,
    user_update: UserUpdate,
    db: db_dependency,
):
    user = user_services.get_user_by_id(db, user_id)
    return user_services.update_user_profile(db, user, user_update)


@router.post(
    "/{user_id}/upload-avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload profile picture",
)
def upload_avatar(
    user_id: int,
    db: db_dependency,
    file: UploadFile = File(...),
):
    user = user_services.get_user_by_id(db, user_id)
    return user_services.upload_profile_picture(db, user, file)


@router.post(
    "/{user_id}/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password",
)
def change_password(
    user_id: int,
    pwd_data: PasswordReset,
    db: db_dependency,
):
    user = user_services.get_user_by_id(db, user_id)
    return user_services.change_user_password(db, user, pwd_data)