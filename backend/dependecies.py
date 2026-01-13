from fastapi.templating import Jinja2Templates
import bcrypt
from pwdlib import PasswordHash
from fastapi.security import (
    OAuth2PasswordBearer,
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

templates = Jinja2Templates(directory="html_templates")
salt = bcrypt.gensalt()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", scheme_name="JWT")
password_hash = PasswordHash.recommended()

