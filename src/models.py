from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from database import Base

# La fonction get_db() est maintenant dans database.py


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), index=True)
    adresse = Column(String(255))
    role = Column(String(50), default="user")
# Pour créer les tables dans la base de donnée