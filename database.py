from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from urllib.parse import quote_plus

# src/database.py
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

# Charge les variables d'environnement depuis .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Récupère l'URL de la base depuis Railway ou .env
raw_url = os.getenv("DATABASE_URL")
if not raw_url:
    raise ValueError(
        "La variable d'environnement DATABASE_URL n'est pas définie. "
        "Vérifiez votre fichier .env ou vos variables Railway."
    )

# Correction du préfixe pour SQLAlchemy + PyMySQL
# Vérifie si l'URL commence par mysql:// et la transforme si nécessaire
DATABASE_URL = raw_url.replace("mysql://", "mysql+pymysql://", 1) if raw_url.startswith("mysql://") else raw_url

# Configuration de l'engine SQLAlchemy avec des paramètres optimisés
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,              # Vérifie la connexion avant utilisation
    pool_recycle=300,                # Recycle les connexions après 5 minutes
    pool_size=10,                    # Taille optimale pour Railway
    max_overflow=20,                 # Connexions supplémentaires autorisées
    pool_timeout=30,                 # Timeout du pool de connexions
    connect_args={
        "connect_timeout": 60        # Timeout de connexion MySQL
    }
)

# Configuration de la session SQLAlchemy
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False           # Évite les problèmes de lazy loading
)

# Base déclarative pour les modèles ORM
Base = declarative_base()

def get_db() -> Generator:
    """
    Dépendance FastAPI pour injecter la session de base de données.
    Assure la fermeture correcte de la session après chaque requête.
    
    Yields:
        Session: Une session SQLAlchemy active
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test de connexion si exécuté directement
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ Connexion à la base de données réussie!")
    except Exception as e:
        print(f"❌ Erreur de connexion : {str(e)}")


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
