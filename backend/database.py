from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.environ.get("postgres_url"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.drop_all(bind=engine)
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
