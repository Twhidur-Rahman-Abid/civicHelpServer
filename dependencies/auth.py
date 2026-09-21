from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db.db import get_db
from models.user import User
from services import user_services
from utils.auth import verify_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/api/auth/login")

DbSession = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(db: DbSession, token: TokenDep) -> User:
    payload = verify_token(token, is_refresh=False)
    user_id_str = payload.get("sub")

    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_services.get_user_by_id(db, int(user_id_str))

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    return user


# Clean type alias for routes
CurrentUser = Annotated[User, Depends(get_current_user)]