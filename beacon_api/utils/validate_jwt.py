"""JSON Token authentication."""

from typing import List, Callable, Set, Tuple, Any
from ..permissions.ga4gh import check_ga4gh_token
from aiocache import cached
from aiocache.serializers import JsonSerializer
from ..api.exceptions import BeaconUnauthorised, BeaconForbidden, BeaconServerError
from aiohttp import web
from authlib.jose import jwt
from authlib.jose.errors import MissingClaimError, InvalidClaimError, ExpiredTokenError, InvalidTokenError, DecodeError
import re
import aiohttp
from os import environ
from .logging import LOG
from ..conf import OAUTH2_CONFIG
from .validate_json import parse_request_object


# This can be something that lives longer as it is unlikely to change
@cached(ttl=3600, key="jwk_key", serializer=JsonSerializer())
async def get_key():
    """Get OAuth2 public key and transform it to usable pem key."""
    existing_key = environ.get("PUBLIC_KEY", None)
    if existing_key is not None:
        return existing_key
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(OAUTH2_CONFIG.server) as r:
                # This can be a single key or a list of JWK
                return await r.json()
    except Exception:
        raise BeaconServerError("Could not retrieve OAuth2 public key.")


def token_scheme_check(token, scheme, obj, host):
    """Check if token has proper scheme and was provided."""
    if not re.match("Bearer", scheme):
        raise BeaconUnauthorised(obj, host, "invalid_token", "Invalid token scheme, Bearer required.")

    if token is None:
        # Might never happen
        raise BeaconUnauthorised(obj, host, "invalid_token", "Token cannot be empty.")  # pragma: no cover


def verify_aud_claim() -> Tuple[Any, Any]:
    """Verify audience claim."""
    aud: List[str] = []
    verify_aud = OAUTH2_CONFIG.verify_aud  # Option to skip verification of `aud` claim
    if verify_aud:
        temp_aud = environ.get("JWT_AUD", OAUTH2_CONFIG.audience)  # List of intended audiences of token
        # if verify_aud is set to True, we expect that a desired aud is then supplied.
        # However, if verify_aud=True and no aud is supplied, we use aud=[None] which will fail for
        # all tokens as a security measure. If aud=[], all tokens will pass (as is the default value).
        if temp_aud is not None:
            aud = temp_aud.split(",")

    return verify_aud, aud


def token_auth() -> Callable:
    """Check if token is valid and authenticate.

    Decided against: https://github.com/hzlmn/aiohttp-jwt, as we need to verify
    token issuer and bona_fide_status.
    """

    @web.middleware
    async def token_middleware(request: web.Request, handler):
        if request.path in ["/query"] and "Authorization" in request.headers:
            _, obj = await parse_request_object(request)
            try:
                # The second item is the token.
                scheme, token = request.headers.get("Authorization", "").split(" ")
                LOG.info("Auth Token Received.")
            except Exception as e:
                raise BeaconUnauthorised(obj, request.host, "invalid_token", str(e))

            token_scheme_check(token, scheme, obj, request.host)

            # Token decoding parameters
            key = await get_key()  # JWK used to decode token with
            verify_aud, aud = verify_aud_claim()
            # Prepare JWTClaims validation
            # can be populated with claims that are required to be present in the payload of the token
            claims_options = {
                "iss": {
                    "essential": True,
                    "values": OAUTH2_CONFIG.issuers.split(","),  # Token allowed from these issuers
                },
                "aud": {"essential": verify_aud, "values": aud},
                "exp": {"essential": True},
            }

            try:
                decoded_data = jwt.decode(token, key, claims_options=claims_options)  # decode the token
                decoded_data.validate()  # validate the token contents
                LOG.info("Auth Token Decoded.")
                LOG.info(f'Identified as {decoded_data["sub"]} user by {decoded_data["iss"]}.')
                # for now the permissions just reflects that the data can be decoded from token
                # the bona fide status is checked against ELIXIR AAI by default or the URL from config
                # the bona_fide_status is specific to ELIXIR Tokens
                # Retrieve GA4GH Passports from /userinfo and process them into dataset permissions and bona fide status
                dataset_permissions: Set[str] = set()
                bona_fide_status: bool = False
                dataset_permissions, bona_fide_status = await check_ga4gh_token(decoded_data, token, bona_fide_status, dataset_permissions)
                # currently we offer module for parsing GA4GH permissions, but multiple claims and providers can be utilised
                # by updating the set, meaning replicating the line below with the permissions function and its associated claim
                # For GA4GH DURI permissions (ELIXIR Permissions API 2.0)
                controlled_datasets: Set[str] = set()
                controlled_datasets.update(dataset_permissions)
                all_controlled = list(controlled_datasets) if bool(controlled_datasets) else None
                request["token"] = {
                    "bona_fide_status": bona_fide_status,
                    # permissions key will hold the actual permissions found in the token/userinfo e.g. GA4GH permissions
                    "permissions": all_controlled,
                    # additional checks can be performed against this authenticated key
                    # currently if a token is valid that means request is authenticated
                    "authenticated": True,
                }
                return await handler(request)
            # Testing the exceptions is done in integration tests
            except MissingClaimError as e:
                raise BeaconUnauthorised(obj, request.host, "invalid_token", f"Missing claim(s): {e}")  # pragma: no cover
            except ExpiredTokenError as e:
                raise BeaconUnauthorised(obj, request.host, "invalid_token", f"Expired signature: {e}")  # pragma: no cover
            except InvalidClaimError as e:
                raise BeaconForbidden(obj, request.host, f"Token info not corresponding with claim: {e}")  # pragma: no cover
            except InvalidTokenError as e:  # pragma: no cover
                raise BeaconUnauthorised(obj, request.host, "invalid_token", f"Invalid authorization token: {e}")  # pragma: no cover
            except DecodeError as e:  # pragma: no cover
                raise BeaconUnauthorised(obj, request.host, "invalid_token", f"Invalid JWT format: {e}")  # pragma: no cover
        else:
            request["token"] = {"bona_fide_status": False, "permissions": None, "authenticated": False}
            return await handler(request)

    return token_middleware
