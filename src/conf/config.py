from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int
    postgres_host: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    mail_server: str
    mail_port: int
    mail_username: str
    mail_password: str
    mail_from: str
    mail_ssl_tls: bool
    mail_starttls: bool
    mail_from_name: str

    redis_host: str
    redis_port: int

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def sqlalchemy_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

settings = Settings()
