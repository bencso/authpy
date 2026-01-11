from datetime import datetime, timedelta, timezone
from typing import Annotated
import segno
import uuid
import urllib.parse
from fastapi import APIRouter, Request, Depends, Response
from middleware import auth_middleware
from database import get_db
from models.User import User
import os
from dependecies import password_hash 
import jwt
from dependecies import templates

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


router = APIRouter(
    prefix="/auth",
    tags=["Authentikacio"],
    responses={
        404: {"description": "Nem található"},
        401: {"description": "Kérjük, jelentkezzen be a művelethez"},
        200: {"description": "Sikeres művelet"},
    },
)


@router.post(
    "/create-temporary-user",
    summary="Temporary QR kód létrehozás",
    description="Az admin felhasználó, létre tud hozni egy temporary qr kódot, amit ha beolvas majd a felhasználó, az átírányítja őt egy forms oldalra, ahol tud regisztrálni",
)
async def create_temporary_qr(
    request: Request, token: Annotated[str, Depends(auth_middleware)]
):
    try:
        print(token)
        random_uid = uuid.uuid4()
        qrcode = segno.make("http://localhost:8001/temporary-qr?q=" + str(random_uid))
        qrcode_svg = qrcode.svg_inline(scale=12, border=2)
        return templates.TemplateResponse(
            request=request, name="qrcode.html", context={"qrcode": qrcode_svg}
        )
    except Exception as e:
        return {"message": "Hiba: " + str(e)}

def verify_token(token):
    try:
        return jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=ALGORITHM)
    except jwt.ExpiredSignatureError:
        return "Token lejárt"
    except jwt.InvalidTokenError:
        return "Invalid a token"
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", summary="Login")
async def login(request: Request, response: Response, db: Annotated[object, Depends(get_db)]):
    try:
        body = await request.body()
        if not body:
            raise ValueError("A bejelentkezés során hiba történt!")
        stringed_body = body.decode("utf-8")
        
        form_data = urllib.parse.parse_qs(stringed_body)
        username = form_data.get("username", [""])[0]
        password = form_data.get("password", [""])[0]
        
        if not username or not password:
            raise ValueError("A felhasználónév és a jelszó kötelező!")
        
        search_user = db.query(User).filter(User.username == username).first()
        if not search_user:
            raise ValueError("A felhasználó nem található!")

        if password_hash.verify(password, search_user.password_hashed):
            token_data = {
                "username": username
            }
            access_token = create_access_token(
                data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            response.set_cookie(
                key="access_token", 
                value=access_token, 
                httponly=True,
                secure=True,
                samesite="lax"
            )
            return {
                "message": "Sikeres bejelentkezés",
                "access_token": access_token,
                "token_type": "bearer"
            }
        else:
            raise ValueError("A bejelentkezési adatok nem egyeznek!")
    except Exception as e:
        return {"message": "Hiba: " + str(e)}
