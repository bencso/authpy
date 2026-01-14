from datetime import datetime, timedelta, timezone
from typing import Annotated, Union
from uuid import uuid4
from fastapi import APIRouter, Depends, Response, HTTPException, status, Form
from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from pydantic import BaseModel
from database import get_db
from models.User import User
import os
from dependecies import password_hash, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import jwt
from functions.auth.get_current_user import get_current_user
from middleware import auth_middleware_admin
from functions.auth.randompassword import get_random_password
from sqlalchemy import func

security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    message: str


router = APIRouter(
    prefix="/auth",
    tags=["Authentikacio"],
    responses={
        404: {"description": "Nem található"},
        401: {"description": "Kérjük, jelentkezzen be a művelethez"},
        200: {"description": "Sikeres művelet"},
    },
)


def verify_token(token):
    try:
        return jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=ALGORITHM)
    except jwt.ExpiredSignatureError:
        return "Token lejárt"
    except jwt.InvalidTokenError:
        return "Érvénytelen a token"


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", summary="Bejelentkezés", response_model=dict)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[object, Depends(get_db)],
    response: Response,
):
    username = form_data.username
    password = form_data.password

    search_user = db.query(User).filter(User.username == username).first()
    if not search_user or not password_hash.verify(
        password, search_user.password_hashed
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Helytelen felhasználónév vagy jelszó",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "username": username,
        "user_id": search_user.id,
        "sub": username,
        "iat": datetime.now(timezone.utc),
        "role": search_user.role if hasattr(search_user, "role") else 0,
    }
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {
        "message": "Sikeres bejelentkezés",
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post(
    "/create-user",
    summary="Új felhasználó készítése adminnal",
    response_model=dict,
)
async def create_user(
    user: Annotated[Union[HTTPException, str], Depends(auth_middleware_admin)],
    username: Annotated[str, Form()],
    db: Annotated[object, Depends(get_db)],
    response: Response,
    password: Annotated[str, Form()] = None,
):
    has_this_username_in_db = (
        db.query(User).filter(func.lower(User.username) == func.lower(username)).first()
    )
    if has_this_username_in_db:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Van már ilyen felhasználónévvel rendelkező felhasználó",
        )
    uuid = uuid4()
    _password = password or await get_random_password()
    hashed_password = password_hash.hash(_password)
    qrcode_data = {
        "sub": str(uuid),
        "username": username,
        "password": hashed_password,
        "iat": datetime.now(timezone.utc),
    }
    qrcode = jwt.encode(qrcode_data, os.getenv("QRCODE_KEY"), algorithm=ALGORITHM)

    new_user = User(
        qrcode=qrcode, username=username, password_hashed=hashed_password, role=0
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Sikeres felhasználó létrehozás: " + new_user.username,
    }


@router.get("/me", summary="Jelenlegi felhasználó adatai")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "username": current_user.username,
        "user_id": current_user.id,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }
