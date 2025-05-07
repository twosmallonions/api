# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from functools import cache

from pydantic import DirectoryPath, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: PostgresDsn
    oidc_well_known: HttpUrl
    data_dir: DirectoryPath
    enable_openapi: bool = True
    http_scraper_user_agent: str = 'tso-api / 0.1.0'


settings = Settings()  # pyright: ignore [reportCallIssue]


@cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore [reportCallIssue]
