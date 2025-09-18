from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Paramètres de configuration pour l'application, chargés à partir d'un fichier .env.
    """
    SECRET_KEY: str  # La clé secrète pour signer les JWT.
    ALGORITHM: str  # L'algorithme à utiliser pour signer les JWT (par exemple, HS256).
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # La durée de vie des jetons d'accès en minutes.

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings(_env_file='c:\\Users\\DELL\\Desktop\\api-fast\\env\\.env')
