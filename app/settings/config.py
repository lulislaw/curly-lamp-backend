# backend/app/settings/config.py

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    KAFKA_BOOTSTRAP_SERVERS: str = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_APPEAL_TOPIC: str = Field(..., env="KAFKA_APPEAL_TOPIC")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
