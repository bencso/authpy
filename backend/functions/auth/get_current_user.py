from typing import Annotated
from fastapi import Depends, HTTPException, status
from database import get_db
from models.User import User
import os
import jwt
from dependecies import  oauth2_scheme,ALGORITHM

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[object, Depends(get_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="A hitelesítő adatok nem érvényesek",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
