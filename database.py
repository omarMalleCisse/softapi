from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from urllib.parse import quote_plus

# Configuration de la base de données avec les variables Railway
DB_HOST = os.getenv("MYSQLHOST", "localhost")
DB_USER = os.getenv("MYSQLUSER", "root")
DB_PASSWORD = os.getenv("MYSQLPASSWORD", "root")
DB_NAME = os.getenv("MYSQLDATABASE", "softwaar")
DB_PORT = os.getenv("MYSQLPORT", "3306")

# Construction de l'URL sécurisée pour MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Créer le moteur avec des paramètres optimisés pour Railway
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,              # Vérifie la connexion avant utilisation
    pool_recycle=300,                # Recycle les connexions après 5 minutes
    pool_size=10,                    # Taille du pool de connexions augmentée
    max_overflow=20,                 # Plus de connexions supplémentaires autorisées
    connect_args={
        "connect_timeout": 30        # Timeout de connexion réduit pour Railway
    }
)

# Configuration de la session et de la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
