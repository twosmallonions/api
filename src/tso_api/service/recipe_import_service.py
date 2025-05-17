from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, overload
from uuid import UUID

import httpx
from psycopg_pool.pool_async import AsyncConnectionPool
from recipe_scrapers import (
    AbstractScraper,
    NoSchemaFoundInWildMode,
    RecipeSchemaNotFound,
    StaticValueException,
    scrape_html,
)

from tso_api.config import get_settings
from tso_api.exceptions import ScrapeRecipeError, ScraperError
from tso_api.import_util import load_concrete_classes_from_pkg
from tso_api.models.recipe import RecipeCreate
from tso_api.models.user import User
from tso_api.service.base_service import BaseService
from tso_api.service.recipe_asset import RecipeAssetService
from tso_api.service.recipe_service import RecipeService


class HTMLScraper(ABC):
    @abstractmethod
    async def scrape_html(self, url: str) -> str: ...

    @property
    @abstractmethod
    def priority(self) -> int: ...


class RecipeImportService(BaseService):
    def __init__(
        self,
        pool: AsyncConnectionPool[Any],
        recipe_service: RecipeService,
        recipe_asset_service: RecipeAssetService,
        user_agent: str,
    ) -> None:
        super().__init__(pool)
        self.recipe_service = recipe_service
        self.recipe_asset_service = recipe_asset_service
        self.html_scrapers: list[HTMLScraper] = []
        self._load_html_scrapers()

        user_agent = get_settings().http_scraper_user_agent
        timeout = httpx.Timeout(10, connect=5, read=20)
        self.http_client = httpx.AsyncClient(
            headers={
                'user-agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            },
            timeout=timeout,
            follow_redirects=True,
        )

    def _load_html_scrapers(self):
        classes = load_concrete_classes_from_pkg('tso_api.service.scraper.html', HTMLScraper)
        scrapers: list[HTMLScraper] = [cls() for cls in classes]  # type: ignore

        scrapers.sort(key=lambda a: a.priority, reverse=True)

        if len(scrapers) == 0:
            msg = 'failed to load any HTML scrapers'
            raise ScraperError(msg)

        self.html_scrapers = scrapers

    async def _scrape_html(self, recipe_url: str) -> str | None:
        for scraper in self.html_scrapers:
            try:
                return await scraper.scrape_html(recipe_url)
            except ScraperError:
                continue
        return None

    async def scrape_and_save_recipe(self, recipe_url: str, user: User, collection_id: UUID):
        html_response = await self._scrape_html(recipe_url)
        if html_response is None:
            msg = 'failed to scrape html'
            raise ScraperError(msg)

        try:
            scraper = scrape_html(html_response, recipe_url, supported_only=False)
        except RecipeSchemaNotFound as e:
            msg = 'recipe schema not found'
            raise ScrapeRecipeError(msg, recipe_url) from e
        except NoSchemaFoundInWildMode as e:
            msg = 'no schema found on the website'
            raise ScrapeRecipeError(msg, recipe_url) from e

        title = _get_str(scraper, 'title')
        if title is None:
            msg = 'failed to extract a title from HTML'
            raise ScrapeRecipeError(msg, recipe_url)

        recipe_create = RecipeCreate(
            title=title,
            note=_get_str(scraper, 'description', ''),
            cook_time=_get_int(scraper, 'cook_time'),
            prep_time=_get_int(scraper, 'prep_time'),
            recipe_yield=_get_str(scraper, 'yields'),
            instructions=_get_field(scraper, 'instructions_list'),
            ingredients=_get_field(scraper, 'ingredients'),
            original_url=recipe_url,
        )
        new_recipe = await self.recipe_service.create(recipe_create, user, collection_id)

        res_image = _get_field(scraper, 'image')
        if res_image is not None:
            res_image = await self.http_client.get(_get_field(scraper, 'image'))
            bytes_io = BytesIO(res_image.content)

            await self.recipe_asset_service.add_cover_image_to_recipe(
                new_recipe.id, new_recipe.collection, user, bytes_io, recipe_url
            )

        return await self.recipe_service.get_by_id(new_recipe.id, user)


def _get_field(scraper: AbstractScraper, field: str, default: Any = None):  # noqa: ANN401
    try:
        fn = getattr(scraper, field)
        return fn()
    except StaticValueException as e:
        return e.return_value
    except:  # noqa: E722 Sometimes a SchemaOrgException is thrown which can't even be imported from RecipeScrapers
        return default


@overload
def _get_str(scraper: AbstractScraper, field: str, default: str) -> str: ...


@overload
def _get_str(scraper: AbstractScraper, field: str) -> str | None: ...


def _get_str(scraper: AbstractScraper, field: str, default: str | None = None):
    value = _get_field(scraper, field, default)

    return str(value) if value is not None else None  # type: ignore[ereportUnknownArgumentType]


def _get_int(scraper: AbstractScraper, field: str, default: int | None = None):
    try:
        return int(_get_field(scraper, field, default))
    except (ValueError, TypeError):
        return None
