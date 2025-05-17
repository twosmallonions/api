import httpx

from tso_api.config import get_settings
from tso_api.service.recipe_import_service import HTMLScraper


class HttpRequestScraper(HTMLScraper):
    def __init__(self) -> None:
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

    async def scrape_html(self, url: str) -> str:
        res = await self.http_client.get(url)

        return res.text

    @property
    def priority(self):
        return 100
