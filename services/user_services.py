import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, UploadFile
from models.user import User
from schemas.user import UserCreate, UserUpdate, PasswordReset
from utils.auth import hash_password, verify_password

UPLOAD_DIR = "static/uploads/profiles"


def register_user(db: Session, user_in: UserCreate) -> User:
    try:
        # 1. Email uniqueness check
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        # 2. Hash password and save
        hashed_pwd = hash_password(user_in.password)
        new_user = User(
            name=user_in.name,
            email=user_in.email,
            password=hashed_pwd,
            phone=user_in.phone
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    except SQLAlchemyError as e:
        db.rollback()

        print(f"REGISTER DB ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while registering user"
        ) from e


def get_user_by_id(db: Session, user_id: int) -> User:
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching user"
        ) from e


def update_user_profile(db: Session, user: User, user_update: UserUpdate) -> User:
    try:
        update_data = user_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating profile"
        ) from e


def upload_profile_picture(db: Session, user: User, file: UploadFile) -> User:
    # 1. Image validation
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image"
        )

    try:
        # 2. Directory creation
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 3. Save with unique file name
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # 4. Save path to profile attribute
        user.profile = f"/{file_path.replace('\\', '/')}"
        db.commit()
        db.refresh(user)
        return user

    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save profile picture to server storage"
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while saving profile image path"
        ) from e


def change_user_password(db: Session, user: User, pwd_data: PasswordReset) -> dict:
    if not verify_password(pwd_data.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    try:
        user.password = hash_password(pwd_data.new_password)
        db.commit()
        return {"message": "Password updated successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating password"
        ) 