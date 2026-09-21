from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from models.user import UserRole





class UserBase(BaseModel):
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="Full name of the user", 
        examples=["Abrar Fahad"]
    )
    email: EmailStr = Field(
        ..., 
        description="Unique email address for login and notifications", 
        examples=["user@example.com"]
    )
    phone: str | None = Field(
        default=None, 
        max_length=20, 
        description="Optional contact telephone or mobile number", 
        examples=["+8801700000000"]
    )


class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=6, 
        max_length=100, 
        description="Raw security password, hashed on backend before storing", 
        examples=["Pass@1234"]
    )


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None, 
        min_length=2, 
        max_length=100, 
        description="Updated full name", 
        examples=["Abrar Fahad Chowdhury"]
    )
    phone: str | None = Field(
        default=None, 
        max_length=20, 
        description="Updated phone number", 
        examples=["+8801800000000"]
    )
    profile: str | None = Field(
        default=None, 
        max_length=255, 
        description="Profile image URL or relative path", 
        examples=["/static/uploads/profiles/avatar_1.jpg"]
    )


class UserResponse(UserBase):
    id: int = Field(
        ..., 
        description="Unique primary key ID of the user", 
        examples=[1]
    )
    role: UserRole = Field(
        ..., 
        description="System access control role", 
        examples=[UserRole.CITIZEN]
    )
    is_active: bool = Field(
        ..., 
        description="Account active status flag", 
        examples=[True]
    )
    profile: str | None = Field(
        default=None, 
        description="Path or URL to the user profile image", 
        examples=["/static/uploads/profiles/avatar_1.jpg"]
    )
    created_at: datetime = Field(
        ..., 
        description="Timestamp when the user account was created", 
        examples=["2026-09-20T12:00:00Z"]
    )
    updated_at: datetime = Field(
        ..., 
        description="Timestamp when the user account was last updated", 
        examples=["2026-09-20T12:00:00Z"]
    )

    model_config = ConfigDict(from_attributes=True)


class PasswordReset(BaseModel):
    old_password: str = Field(
        ..., 
        description="Current user password for verification", 
        examples=["OldPass123"]
    )
    new_password: str = Field(
        ..., 
        min_length=6, 
        max_length=100, 
        description="New password to set", 
        examples=["NewPass456"]
    )