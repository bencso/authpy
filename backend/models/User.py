from backend.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text


class User(Base):
    __tablename__="users"
    
    id = Column(Integer,primary_key=True,nullable=False)
    qrcode = Column(String, nullable=True, default="ideinglenes_"+id)
    username = Column(String, nullable=True)
    passwordHashed = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))