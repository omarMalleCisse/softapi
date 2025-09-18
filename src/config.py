from typing import Optional
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """
    Paramètres de configuration pour l'application.
    Ces paramètres sont chargés depuis les variables d'environnement
    ou le fichier .env
    """
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = True

# Instance des paramètres
settings = Settings()
