from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .. import crud, models
from ..dependencies import SessionDep
from ..models import User, UserCreate, UserRead
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, session: SessionDep) -> User:
    # create a new user
    return crud.create_user(session, email=payload.email, password=payload.password)


"""
What is OAuth2PasswordRequestForm?
It is a FastAPI class that automatically extracts login credentials sent as form data.
"""


@router.post("/token")
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> models.AccessToken:

    # get the user name
    user_name = form_data.username
    password = form_data.password
    user = crud.get_user_by_email(session, user_name)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password",
            headers={"WWW-Auhtenticate": "bearer"},
        )
    # generate JWT
    access_token = create_access_token(subject=str(user.id), expires_delta=None)
    return models.AccessToken(access_token=access_token, token_type="bearer")
