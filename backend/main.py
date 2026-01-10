from http.client import HTTPException
from typing import Annotated
from fastapi import FastAPI, Depends, APIRouter, status, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, db_dependency
from routers import users


app = FastAPI()
Base.metadata.create_all(bind=engine)

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
    responses={404: {"description": "Nem található"}, 401: {"description": "Kérjük, jelentkezzen be a művelethez"}},
)
    
@apirouter.get("/test", tags=["Teszt"])
def get_hello():
    return "TEST!"

apirouter.include_router(users.router)
app.include_router(apirouter)