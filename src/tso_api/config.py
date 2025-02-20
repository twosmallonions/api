from pydantic import HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    database_url: PostgresDsn
    oidc_well_known: HttpUrl


settings = Settings()  # pyright: ignore [reportCallIssue]
