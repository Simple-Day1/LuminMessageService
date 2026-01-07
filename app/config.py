from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr


class Settings(BaseSettings):
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="LuminMessageDatabase", env="DB_NAME")
    db_user: str = Field(default="postgres", env="DB_USER")
    db_password: SecretStr = Field(default="(123)%111", env="DB_PASSWORD")

    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: SecretStr = Field("", env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")

    nats_url: str = Field(default="nats://localhost:4222", env="NATS_URL")

    app_env: str = Field(default="development", env="APP_ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")

    class Config:
        env_file = "LuminMessageService.env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        @classmethod
        def customise_sources(
                cls,
                init_settings,
                env_settings,
                file_secret_settings,
        ):
            return (
                init_settings,
                file_secret_settings,
                env_settings,
            )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

db_password = settings.db_password.get_secret_value()
redis_password = settings.redis_password.get_secret_value()
