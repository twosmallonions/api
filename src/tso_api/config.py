from typing import final
from pydantic import DirectoryPath, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    database_url: PostgresDsn
    oidc_well_known: HttpUrl
    jwt_algorithms: list[str] = ['RS256']
    data_dir: DirectoryPath


settings = Settings()  # pyright: ignore [reportCallIssue]
print(settings.jwt_algorithms)
