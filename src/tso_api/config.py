# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from pydantic import DirectoryPath, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    database_url: PostgresDsn
    oidc_well_known: HttpUrl
    jwt_algorithms: list[str] = ['RS256']
    data_dir: DirectoryPath
    enable_openapi: bool = True


settings = Settings()  # pyright: ignore [reportCallIssue]
