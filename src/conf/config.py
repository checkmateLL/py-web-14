from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Union

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
    mail_username:  Union[str, SecretStr]
    mail_password:  Union[str, SecretStr]
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

    def __init__(self, **data):
        # Explicitly convert SecretStr to string if needed
        if isinstance(data.get('mail_username'), SecretStr):
            data['mail_username'] = data['mail_username'].get_secret_value()
        if isinstance(data.get('mail_password'), SecretStr):
            data['mail_password'] = data['mail_password'].get_secret_value()
        super().__init__(**data)      

    @property
    def sqlalchemy_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

settings = Settings()
