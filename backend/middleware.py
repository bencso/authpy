from typing import Annotated
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models.User import User
from routers.auth import get_current_user
from dependecies import oauth2_scheme


def auth_middleware(token: Annotated[str, Depends(oauth2_scheme)]):
    if token == "undefined" or token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="A bejelentkezés szükséges"
        )
    return token


def auth_middleware_admin(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="A bejelentkezés szükséges",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token == "undefined" or token is None:
        raise credentials_exception
    if current_user.role != "1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="A művelethez nincs megfelelő jogosultsága"
        )
    return token
