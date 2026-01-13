from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models.User import User
from routers import auth
from dependecies import password_hash
from uuid import uuid4
from datetime import datetime

app = FastAPI(
    title="Homestant API",
    description="API dokumentáció a Homestant alkalmazáshoz",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)
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
    responses={
        404: {"description": "Nem található"},
        401: {"description": "Kérjük, jelentkezzen be a művelethez"},
        200: {"description": "Sikeres művelet"},
    },
)


ADMIN_USERNAME = "admin"


async def create_admin_user_on_startup(db: Session):
    uuid = uuid4()
    hashed_password = password_hash.hash("Adminjelszó123")
    has_admin_user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    if has_admin_user is not None:
        raise ValueError("Van már ilyen admin felhasználó")
    else:
        admin_user = User(
            qrcode=uuid,
            username=ADMIN_USERNAME,
            password_hashed=hashed_password,
            created_at=datetime.now(),
            role=1,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        return admin_user


@app.on_event("startup")
async def startup():
    db = next(get_db())
    try:
        await create_admin_user_on_startup(db)
    finally:
        db.close()
    yield


@apirouter.post("/create-admin", tags=["Teszt"])
async def add_admin_user(db: Session = Depends(get_db)):
    try:
        await create_admin_user_on_startup(db=db)
        return {"message": "Sikeres admin létrehozás"}
    except Exception as e:
        return {"message": str(e)}


@apirouter.delete("/delete-admin", tags=["Teszt"])
async def delete_admin_user(db: Session = Depends(get_db)):
    admin_user = db.query(User).filter(User.username == "admin").first()
    if admin_user:
        db.delete(admin_user)
        db.commit()
        return {"message": "Admin felhasználó törölve"}
    return {"message": "Nincs admin felhasználó"}


apirouter.include_router(auth.router)
app.include_router(apirouter)
