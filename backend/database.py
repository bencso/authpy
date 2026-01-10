from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi import Depends
import os
from typing import Annotated

load_dotenv()
engine = create_engine(os.environ.get("postgres_url"))
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
db_dependency = Annotated[SessionLocal,Depends(get_db)]