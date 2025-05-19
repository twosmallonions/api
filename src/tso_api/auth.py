# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from functools import cached_property
from typing import Annotated

import httpx
import jwt
from fastapi import Depends
from fastapi.security import OpenIdConnect
from jwt import ExpiredSignatureError, InvalidKeyError, InvalidTokenError, PyJWKClient
from pydantic import BaseModel, Field, HttpUrl

from tso_api import config
from tso_api.exceptions import AuthenticationError


class OIDCWellKnown(BaseModel):
    issuer: str
    jwks_uri: HttpUrl
    id_token_signing_alg_values_supported: list[str]


class JWT(BaseModel):
    issuer: str = Field(validation_alias='iss')
    subject: str = Field(validation_alias='sub')
    preferred_username: str | None
    email: str | None
    name: str | None
    given_name: str | None


AUTHORIZATION_HEADER_PARTS = 2


oidc_scheme = OpenIdConnect(openIdConnectUrl=str(config.get_settings().oidc_well_known))


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

    def __call__(self, authorization: Annotated[str, Depends(oidc_scheme)]) -> JWT:
        split = authorization.split(' ', 1)
        if len(split) != AUTHORIZATION_HEADER_PARTS:
            msg = 'invalid authorization header'
            raise AuthenticationError(msg)

        if split[0] != 'Bearer':
            msg = 'invalid authorization scheme'
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
            raise AuthenticationError(str(e), 'invalid_token', 'invalid signing key') from None
        except ExpiredSignatureError as e:
            raise AuthenticationError(str(e), 'invalid_token', 'token expired') from None
        except InvalidTokenError as e:
            raise AuthenticationError(str(e), 'invalid_token', 'token invalid') from None

        return JWT.model_validate(verified_jwt)
