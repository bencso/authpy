from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from models.User import User
from routers import auth
from dependecies import password_hash
from uuid import uuid4
from datetime import datetime
from database import SessionLocal

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
    responses={
        404: {"description": "Nem található"},
        401: {"description": "Kérjük, jelentkezzen be a művelethez"},
        200: {"description": "Sikeres művelet"},
    },
)

@app.on_event("startup")
async def create_admin_on_startup():
    db = SessionLocal()
    try:
        uuid = uuid4()
        password_hashed = password_hash.hash("Adminjelszó123".encode("utf-8"))
        has_admin_user = db.query(User).filter(User.username == "admin").first()
        if has_admin_user is None:
            admin_user = User(
                id=1,
                qrcode=uuid,
                username="admin",
                password_hashed=password_hashed,
                created_at=datetime.now(),
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Admin felhasználó létrehozva")
        else:
            print("Admin felhasználó már létezik")
    finally:
        db.close()


@apirouter.get("/test", tags=["Teszt"])
def get_hello():
    return "TEST!"


apirouter.include_router(auth.router)
app.include_router(apirouter)
