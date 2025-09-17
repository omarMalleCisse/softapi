from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src import crud, models, schemas
from src.config import settings
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Vérifie un mot de passe en clair par rapport à un mot de passe haché."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hache un mot de passe."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crée un nouveau jeton d'accès.

    Args:
        data: Les données à encoder dans le jeton.
        expires_delta: Le temps d'expiration du jeton.

    Returns:
        Le jeton d'accès encodé.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Décode le jeton JWT pour obtenir l'utilisateur actuel.

    Args:
        db: La session de base de données.
        token: Le jeton JWT.

    Returns:
        L'utilisateur actuel.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_admin(current_user: models.User = Depends(get_current_user)):
    """
    Vérifie si l'utilisateur actuel est un administrateur.

    Args:
        current_user: L'utilisateur actuel

    Returns:
        L'utilisateur actuel s'il est administrateur

    Raises:
        HTTPException: Si l'utilisateur n'est pas un administrateur ou n'est pas actif
    """
    if not current_user.role or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have admin privileges"
        )
    return current_user
