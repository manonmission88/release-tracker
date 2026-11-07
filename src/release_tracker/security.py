from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import Session

from . import models
from .config import get_settings
from .database import get_session

"""
PasswordHash.recommended() returns a configured hasher with sensible defaults.

get_password_hash produces the hash to store in the database;

verify_password checks a candidate password against a stored hash and returns a boolean.


"""
ACCOUNT_TOKEN_EXPIRE = 60
JWT_ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()
security_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(*, subject: str, expires_delta: timedelta | None) -> str:
    expires_at = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCOUNT_TOKEN_EXPIRE))
    payload = {
        "sub": subject,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        get_settings().jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )


def get_current_user(
    token: Annotated[str, Depends(security_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> models.User:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldnot validated credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
        )
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (InvalidTokenError, ValueError) as exc:
        raise credentials_exception from exc  # user doesnot have to know the server side
    user = session.get(models.User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user
