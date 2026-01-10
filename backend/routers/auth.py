from typing import Annotated
import segno
import uuid
from fastapi import APIRouter, Request, Depends
import bcrypt
from middleware import auth_middleware
from dependecies import salt, templates

router = APIRouter(
    prefix="/auth",
    tags=["Authentikacio"],
    responses={404: {"description": "Nem található"}, 401: {"description": "Kérjük, jelentkezzen be a művelethez"}, 200: {"description":"Sikeres művelet"}},
)

@router.post("/create-temporary-user", 
             summary="Temporary QR kód létrehozás", 
             description="Az admin felhasználó, létre tud hozni egy temporary qr kódot, amit ha beolvas majd a felhasználó, az átírányítja őt egy forms oldalra, ahol tud regisztrálni")
async def create_temporary_qr(request: Request, token: Annotated[str, Depends(auth_middleware)]):
    try:
        print(token)
        random_uid=uuid.uuid4()
        #TODO: Admin felhasználó check, az után pedig majd még ide kell, 
        # egy olyan hogy ez a random uuid-t felteszem db-be és frontenden csinálni neki egy felületet forms-nak és oda irányít majd a qrcode
        qrcode = segno.make("http://localhost:8001/temporary-qr?q="+str(random_uid))
        qrcode_svg = qrcode.svg_inline(scale=12, border=2)
        return templates.TemplateResponse(
            request=request, name='qrcode.html', context={"qrcode": qrcode_svg})   
    except Exception as e:
        return {
           "detail": "Hiba: " + str(e)
       }

    
@router.post("/login", 
             summary="Login")
async def login(request: Request):
    try:
        body = await request.body()
        if(body is None):
            raise ValueError("A bejelentkezés során hiba történt!")
        stringed_body = body.decode("utf-8")
        [_, b_uname, b_pass] = stringed_body.split('&')
        username = b_uname.split("=").pop(-1)
        password = b_pass.split("=").pop(-1).encode("utf-8")
        if(len(username)<= 0 or len(password)<=0):
             raise ValueError("A felhasználónév és a jelszó kötelező!")
        hashed_password = bcrypt.hashpw(password,salt)
        return {
            "access_token": "FAF",
        }
    except Exception as e:
         return {
           "detail": "Hiba: " + str(e)
       }