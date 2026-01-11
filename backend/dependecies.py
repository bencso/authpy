from fastapi.templating import Jinja2Templates
import bcrypt
from pwdlib import PasswordHash

templates = Jinja2Templates(directory="html_templates")
salt = bcrypt.gensalt()

password_hash = PasswordHash.recommended()