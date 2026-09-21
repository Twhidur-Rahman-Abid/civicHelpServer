from pydantic import BaseModel, Field, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="Registered user email address", 
        examples=["user@example.com"]
    )
    password: str = Field(
        ..., 
        min_length=6, 
        max_length=100, 
        description="User password for authentication", 
        examples=["Pass@1234"]
    )

class TokenResponse(BaseModel):
    access_token: str = Field(
        ..., 
        description="JWT access token required for API authentication", 
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    refresh_token: str = Field(
        ..., 
        description="JWT refresh token used to generate a new access token", 
        examples=["dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4..."]
    )
    token_type: str = Field(
        default="bearer", 
        description="Type of authorization token provided", 
        examples=["bearer"]
    )

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        ..., 
        description="Valid JWT refresh token", 
        examples=["dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4..."]
    )