from typing import Annotated
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import User
from db import engine, SessionLocal, Base
import segno

app = FastAPI()
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="html_templates")

def get_db():
    db = SessionLocal()
    try:
        """ 
        - yield: visszaad egy értéket, de a függvény állapota megmarad, és később onnan folytatódik
        
        - PÉLDA:
        def g():
           yield 1
           yield 2
           yield 3
        gen = g()
        next(gen)  # 1
        next(gen)  # 2
        next(gen)  # 3
        """
        yield db
    finally:
        db.close()
        
# Mielött meghívná a @app.get() vagy bármit hívja meg a get_db-t
# A Depends egy jelölő, ami megmondja a FastAPI-nak -> ezt a paramétert ne a requestből vedd, hanem ebből a függvényből.
db_dependency = Annotated[Session,Depends(get_db)]

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_hello():
    return "/docs"

@app.get("/temporary-qr")
async def createTemporayQr(request: Request):
    qrcode = segno.make("http://localhost:8001/temporary-qr")
    qrcode_svg = qrcode.svg_inline(scale=8, border=2)
    return templates.TemplateResponse(
        request=request, name='qrcode.html', context={"qrcode": qrcode_svg})