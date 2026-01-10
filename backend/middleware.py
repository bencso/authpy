from typing import Annotated
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

ouauth_security = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")

def auth_middleware(token: Annotated[str, Depends(ouauth_security)]):
    if token == "undefined" or token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A bejelentkezés szükséges"
        )
    return token