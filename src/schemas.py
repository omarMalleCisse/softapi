from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    """Schéma pour la création d'un nouvel utilisateur."""
    email: str
    password: str
    role: str = "user"  # Champ role par défaut = "user"
    name: str           # <-- Ajouté
    adresse: str        # <-- Ajouté


class User(BaseModel):
    """Schéma pour le retour des informations sur l'utilisateur."""
    id: int
    email: str
    role: str
    name: str           # <-- Ajouté
    adresse: Optional[str] = None        # <-- Ajouté

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schéma pour le jeton d'accès."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schéma pour les données encodées dans le JWT."""
    email: str | None = None


class Login(BaseModel):
    """Schéma pour la connexion de l'utilisateur."""
    username: str
    password: str
