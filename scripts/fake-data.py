# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "faker",
#     "faker-food",
#     "httpx",
# ]
# ///

# ruff: noqa: S311

import os
import httpx
from httpx import Client
from faker import Faker
from faker_food import FoodProvider
import random
from uuid import UUID
from typing import Any


def main() -> None:
    api_base_url = os.environ['API_URL']
    username = os.environ['API_USERNAME']
    password = os.environ['API_PASSWORD']
    client = os.environ['API_OIDC_CLIENT_ID']
    client_secret = os.environ.get('API_OIDC_CLIENT_SECRET', None)
    oidc_token_endpoint = os.environ['API_TOKEN_ENDPOINT']
    create_n_recipes = int(os.environ.get('API_CREATE_N', '10'))
    http_client = httpx.Client(timeout=10.0)

    fake = Faker()
    fake.add_provider(FoodProvider)

    access_token = get_access_token(username, password, oidc_token_endpoint, client, http_client)
    default_collection_id = get_default_collection(api_base_url, access_token, http_client)
    add_recipes(default_collection_id, access_token, create_n_recipes, fake, api_base_url, http_client)


def add_recipes(collection_id: str, access_token: str, create_n: int, fake, api_base_url: str, http: Client):
    for i in range(create_n):
        print(f'Creating {i + 1}/{create_n}')
        recipe = make_recipe(fake)
        add_recipe(recipe, collection_id, access_token, api_base_url, http)


def add_recipe(recipe: dict[str, Any], collection_id: str, access_token: str, api_base_url: str, http: Client):
    resp = http.post(
        f'{api_base_url}/api/recipe/{collection_id}', json=recipe, headers={'Authorization': f'Bearer {access_token}'},
    )
    resp.raise_for_status()


def make_recipe(fake):
    return {
        'title': fake.dish(),
        'note': fake.dish_description(),
        'cookTime': random.randrange(5, 300),
        'prepTime': random.randrange(5, 300),
        'recipeYield': f'{random.randrange(1, 10)} servings',
        'liked': bool(random.randrange(0, 2)),
        'original_url': 'https://example.com/',
        'instructions': [fake.paragraph() for _ in range(random.randrange(3, 20))],
        'ingredients': [fake.ingredient() for _ in range(random.randrange(2, 30))],
    }


def get_default_collection(api_base_url, access_token: str, http: Client) -> UUID:
    resp = http.get(f'{api_base_url}/api/collection/', headers={'Authorization': f'Bearer {access_token}'})
    resp.raise_for_status()

    collections: list[dict[str, Any]] = resp.json()

    for collection in collections:
        if collection['name'] == 'Default':
            return collection['id']

    msg = 'no default collection found'
    raise RuntimeError(msg)


def get_access_token(username: str, password: str, token_endpoint: str, client_id: str, http: Client) -> str:
    params = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'scope': 'openid',
        'client_id': client_id,
    }

    resp = http.post(token_endpoint, data=params)
    resp.raise_for_status()

    return resp.json()['access_token']


if __name__ == '__main__':
    main()
