from pydantic import DirectoryPath, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    postgres_username: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_db: str = "tso"
    postgres_port: int = 5432
    oidc_well_known: HttpUrl
    jwt_algorithms: list[str] = ['RS256']
    data_dir: DirectoryPath
    enable_openapi: bool = True


settings = Settings()  # pyright: ignore [reportCallIssue]
