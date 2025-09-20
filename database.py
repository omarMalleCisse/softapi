from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from urllib.parse import quote_plus

# src/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Récupère l'URL de la base depuis Railway
raw_url = os.getenv("DATABASE_URL")
if not raw_url:
    raise RuntimeError("La variable d'environnement DATABASE_URL n'est pas définie")

# Correction du préfixe pour SQLAlchemy + PyMySQL
DATABASE_URL = raw_url.replace("mysql://", "mysql+pymysql://", 1)

# Crée l’engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crée une session locale pour les transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour définir les modèles ORM
Base = declarative_base()

# Dépendance FastAPI pour injecter la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Exemple de modèle
def create_tables():
    Base.metadata.create_all(bind=engine)

class Branding(Base):
    __tablename__ = "branding"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    image = Column(String(255), unique=True, index=True)

class Features(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True, index=True)
    alt = Column(String(255), index=True)
    image = Column(String(255), unique=True, index=True)
    title = Column(String(255), unique=True, index=True)
    text = Column(String(255), unique=True, index=True)

class BulletPoints(Base):
    __tablename__ = "bullet_points"
    id = Column(Integer, primary_key=True, index=True)
    alt = Column(String(255), index=True)
    image = Column(String(255), unique=True, index=True)
    title = Column(String(255), unique=True, index=True)
    text = Column(String(255), unique=True, index=True)
   


# La classe User a été déplacée vers src/models.py

class Social(Base):
    __tablename__ = "social"
    id = Column(Integer, primary_key=True, index=True)
    ico = Column(String(255), index=True)
    alt = Column(String(255), unique=True, index=True)
    link = Column(String(255), unique=True, index=True)

class Register(Base):
    __tablename__ = "registers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    info = Column(String(255))
    email = Column(String(255), index=True)
    telephone = Column(String(50), index=True)
    adresse = Column(String(255), index=True)


# --- Nouveau modèle Realisation ---
class Realisation(Base):
    __tablename__ = "realisations"
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(String(500), nullable=False)
    image = Column(String(500), nullable=False)
    lien = Column(String(255), nullable=True)



if __name__ == "__main__":
    try:
        # Test de connexion
        with engine.connect() as connection:
            print("Connexion à la base de données réussie !")
        # Création des tables
        create_tables()
        print("Tables créées avec succès !")
    except Exception as e:
        print(f"Erreur de connexion : {e}")
