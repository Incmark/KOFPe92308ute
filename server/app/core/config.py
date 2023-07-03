import pathlib

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator
from typing import List, Optional, Union
from dotenv import load_dotenv
from os import environ

ROOT = pathlib.Path(__file__).resolve().parent.parent
load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    JWT_SECRET: str = environ.get('JWT_SECRET')
    RABBITMQ_URI: str = environ.get('RABBITMQ_URI')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SQLALCHEMY_DATABASE_URI: Optional[str] = environ.get('SQLALCHEMY_DATABASE_URI')
    FIRST_SUPERUSER: EmailStr = "admin@recipeapi.com"
    FIRST_SUPERUSER_PW: str = "CHANGEME"

    class Config:
        case_sensitive = True

settings = Settings()
