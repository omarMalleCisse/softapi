from sqlalchemy.orm import Session

from database import SessionLocal
from src import models, schemas
from src.security import get_password_hash


def get_user_by_email(db: Session, email: str):
    """
    Récupère un utilisateur de la base de données par e-mail.

    Args:
        db: La session de base de données.
        email: L'e-mail de l'utilisateur à récupérer.

    Returns:
        L'utilisateur avec l'e-mail spécifié.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Crée un nouvel utilisateur dans la base de données.

    Args:
        db: La session de base de données.
        user: L'utilisateur à créer.

    Returns:
        L'utilisateur créé.
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email,
                           hashed_password=hashed_password, 
                           role=user.role, name=user.name,        
                           adresse=user.adresse )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user