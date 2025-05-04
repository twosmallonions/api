from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ApiHttpError(BaseModel):
    error: str
    detail: Any
    id: str


class ApiError(Exception):
    status = 500

    def detail(self) -> Any:  # noqa: ANN401, PLR6301
        return None

    def http_headers(self) -> dict[str, str]:
        return {}

    def error_id(self) -> str:
        return self.__class__.__name__


class AuthenticationError(ApiError):
    """Indicates an error with Authentication (JWT couldn't be verified, Auth header could not be parsed)."""

    www_authenticate_error: str | None
    error_description: str | None
    msg = 'Authentication failed'
    status = 401

    def __init__(self, error_message: str, error: str | None = None, error_description: str | None = None) -> None:
        self.www_authenticate_error = error
        self.error_description = error_description
        self.error_message = error_message
        super().__init__(self.msg)

    def http_headers(self) -> dict[str, str]:
        www_authenticate_header = 'Bearer realm="tso"'
        if self.www_authenticate_error:
            www_authenticate_header += f' error="{self.www_authenticate_error}"'

        if self.error_description:
            www_authenticate_header += f' error_description="{self.error_description}"'

        return {'www-authenticate': www_authenticate_header}


class ScraperError(ApiError):
    """Indicates an error with the setup of the scraper (failed to connect to the network while scraping HTML, ...)."""


class ScrapeRecipeError(ApiError):
    """
    Indicates that a recipe could not be scraped because the we couldn't
    get the HTML or the scraper implementation couldn't parse the recipe.
    """

    status = 400

    def __init__(self, msg: str, recipe_url: str) -> None:
        super().__init__(msg)
        self.recipe_url = recipe_url

    def detail(self):
        return {'url': self.recipe_url}


class NoneAfterInsertError(ApiError):
    msg = '{} was inserted but returned None'

    def __init__(self, resource: str) -> None:
        super().__init__(self.msg.format(resource))


class NoneAfterUpdateError(ApiError):
    msg = 'resource {} with id {} was updated but returned None'

    def __init__(self, resource: str, resource_id: UUID) -> None:
        super().__init__(self.msg.format(resource, resource_id))


class ResourceNotFoundError(ApiError):
    msg: str = 'resource not found: {0}'
    resource: str
    status = 400

    def __init__(self, resource: str) -> None:
        self.resource = resource
        super().__init__(self.msg.format(resource))
