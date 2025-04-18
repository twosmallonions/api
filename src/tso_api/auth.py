from functools import cached_property
from typing import Annotated, final

import httpx
import jwt
from fastapi import Depends, Header
from jwt import ExpiredSignatureError, InvalidKeyError, InvalidTokenError, PyJWKClient
from pydantic import BaseModel, HttpUrl

from tso_api.config import settings
from tso_api.models.user import User
from tso_api.service import user_service


class OIDCWellKnown(BaseModel):
    issuer: str
    jwks_uri: HttpUrl
    id_token_signing_alg_values_supported: list[str]


class JWT(BaseModel):
    iss: str
    sub: str
    email: str
    preferred_username: str


@final
class AuthenticationError(Exception):
    www_authenticate_error: str | None
    error_description: str | None
    msg = 'Authentication failed: {}'

    def __init__(self, error_message: str, error: str | None = None, error_description: str | None = None) -> None:
        self.www_authenticate_error = error
        self.error_description = error_description
        super().__init__(self.msg.format(error_message))


AUTHORIZATION_HEADER_PARTS = 2


class OIDCAuth:
    well_known_url: str
    http_client: httpx.Client
    audience: str
    jwks_client: PyJWKClient

    def __init__(self, well_known_url: str, audience: str = 'tso-api') -> None:
        self.well_known_url = well_known_url
        self.http_client = httpx.Client(headers={'user-agent': 'tso-api / 0.1.0'})
        self.audience = audience

        self.jwks_client = PyJWKClient(str(self.well_known.jwks_uri), headers={'user-agent': 'tso-api / 0.1.0'})
        self.jwks_client.fetch_data()

    @cached_property
    def well_known(self) -> OIDCWellKnown:
        res = self.http_client.get(self.well_known_url)
        res.raise_for_status()

        return OIDCWellKnown.model_validate(res.json())

    @property
    def issuer(self) -> str:
        return self.well_known.issuer

    def __call__(self, authorization: Annotated[str | None, Header()] = None) -> JWT:
        if authorization is None:
            msg = 'no authorization header'
            print(msg)
            raise AuthenticationError(msg)

        split = authorization.split(' ', 1)
        if len(split) != AUTHORIZATION_HEADER_PARTS:
            msg = 'invalid authorization header'
            print(msg)
            raise AuthenticationError(msg)

        if split[0] != 'Bearer':
            msg = 'invalid authorization scheme'
            print(msg)
            raise AuthenticationError(msg)

        token = split[1]
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            verified_jwt = jwt.decode(
                token,
                signing_key,
                self.well_known.id_token_signing_alg_values_supported,
                {
                    'require': ['exp', 'sub', 'iss', 'aud'],
                    'verify_aud': False,
                    'verify_issuer': True,
                    'verify_exp': True,
                },
                audience=self.audience,
                issuer=self.issuer,
                leeway=20,
            )
        except InvalidKeyError as e:
            print(e)
            raise AuthenticationError(str(e), 'invalid_token', 'invalid signing key') from None
        except ExpiredSignatureError as e:
            print(e)
            raise AuthenticationError(str(e), 'invalid_token', 'token expired') from None
        except InvalidTokenError as e:
            print(e)
            raise AuthenticationError(str(e), 'invalid_token', 'token invalid') from None

        return JWT.model_validate(verified_jwt)


oidc_auth = OIDCAuth(str(settings.oidc_well_known))


async def get_user(jwt: Annotated[JWT, Depends(oidc_auth)]) -> User:
    return await user_service.get_or_create_user(jwt.sub, jwt.iss)
