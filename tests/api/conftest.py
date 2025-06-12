from typing import Callable
from uuid import uuid4
import httpx
import pytest

from tso_api.models.collection import CollectionCreate


def pytest_addoption(parser: pytest.Parser):
    parser.addoption('--base-url', action='store', default='http://localhost:8000', help='The API base url')
    parser.addoption('--oidc-username', action='store', default='test', help='The username to use for tests')
    parser.addoption('--oidc-password', action='store', default='test', help='The password to use for tests')
    parser.addoption(
        '--oidc-client-id', action='store', help='The client ID of the OIDC client to use (needs to be a public client)', required=True
    )
    parser.addoption(
        '--oidc-token-endpoint', action='store', help='The oauth2 token endpoint for requesting an access token', required=True
    )


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest):
    return request.config.getoption('--base-url')


@pytest.fixture(scope="session")
def oidc_username(request: pytest.FixtureRequest):
    return request.config.getoption('--oidc-username')


@pytest.fixture(scope="session")
def oidc_password(request: pytest.FixtureRequest):
    return request.config.getoption('--oidc-password')


@pytest.fixture(scope="session")
def oidc_client_id(request: pytest.FixtureRequest):
    return request.config.getoption('--oidc-client-id')


@pytest.fixture(scope="session")
def oidc_token_endpoint(request: pytest.FixtureRequest):
    return request.config.getoption('--oidc-token-endpoint')


@pytest.fixture(scope='session')
def base_client():
    return httpx.Client()


@pytest.fixture(scope='module')
def token(
    base_client: httpx.Client, oidc_token_endpoint: str, oidc_username: str, oidc_password: str, oidc_client_id: str
):
    params = {
        'grant_type': 'password',
        'username': oidc_username,
        'password': oidc_password,
        'scope': 'openid',
        'client_id': oidc_client_id,
    }

    resp = base_client.post(oidc_token_endpoint, data=params)
    resp.raise_for_status()

    return resp.json()['access_token']


@pytest.fixture(scope='module')
def client(token: str, base_url: str):
    base_headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

    return httpx.Client(base_url=base_url, headers=base_headers, follow_redirects=True)


UUID4Factory = Callable[[], str]


@pytest.fixture
def uuid4_factory():
    def _do():
        return str(uuid4())

    return _do


@pytest.fixture
def collection(client: httpx.Client, uuid4_factory: UUID4Factory):
    collection_name = uuid4_factory()
    collection_create = CollectionCreate(name=collection_name)

    response = client.post('/api/collection', json=collection_create.model_dump())
    response.raise_for_status()

    return response.json()
