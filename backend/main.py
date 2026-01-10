from typing import Annotated
from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import engine, SessionLocal, Base
from routers import users


app = FastAPI()
Base.metadata.create_all(bind=engine)

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



apirouter = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)

@apirouter.get("/test", tags=["Teszt"])
def get_hello():
    return "TEST!"

apirouter.include_router(users.router)
app.include_router(apirouter)