from typing import Annotated
import segno
import uuid
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
import bcrypt

templates = Jinja2Templates(directory="html_templates")
ouauth_security = OAuth2PasswordBearer(tokenUrl="api/v1/users/check-token")
salt = bcrypt.gensalt()

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create-temporary-user", summary="Temporary QR kód létrehozás", description="Az admin felhasználó, létre tud hozni egy temporary qr kódot, amit ha beolvas majd a felhasználó, az átírányítja őt egy forms oldalra, ahol tud regisztrálni")
async def create_temporary_qr(request: Request,token: Annotated[str, Depends(ouauth_security)]):
    random_uid=uuid.uuid4()
    #TODO: Admin felhasználó check, az után pedig majd még ide kell, 
    # egy olyan hogy ez a random uuid-t felteszem db-be és frontenden csinálni neki egy felületet forms-nak és oda irányít majd a qrcode
    qrcode = segno.make("http://localhost:8001/temporary-qr?q="+str(random_uid))
    qrcode_svg = qrcode.svg_inline(scale=12, border=2)
    return templates.TemplateResponse(
        request=request, name='qrcode.html', context={"qrcode": qrcode_svg})
    
@router.post("/check-token", summary="Token check")
async def check_token(request: Request):
    try:
        body = await request.body()
        if(body is None):
            pass
        stringed_body = body.decode("utf-8")
        [_, b_uname, b_pass] = stringed_body.split('&')
        username = b_uname.split("=").pop(-1)
        password = b_pass.split("=").pop(-1).encode("utf-8")
        if(len(username)<= 0 or len(password)<=0):
            pass
        hashed_password = bcrypt.hashpw(password,salt)
        #TODO: Majd itt checkolni hogy tényleg létezik e ilyen user :) és ezalapján visszaadni
        return "sikeres"
    except:
        print("HIBA, a checkolás során!")
        return False