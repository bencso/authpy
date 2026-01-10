from fastapi.templating import Jinja2Templates
import bcrypt
from database import get_db, SessionLocal
from fastapi import Depends
from typing import Annotated

templates = Jinja2Templates(directory="html_templates")
salt = bcrypt.gensalt()

# Mielött meghívná a @app.get() vagy bármit hívja meg a get_db-t
# A Depends egy jelölő, ami megmondja a FastAPI-nak -> ezt a paramétert ne a requestből vedd, hanem ebből a függvényből.
db_dependency = Annotated[SessionLocal,Depends(get_db)]