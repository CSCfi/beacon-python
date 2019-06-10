"""JSON Request/Response Validation and Token authentication."""

from aiohttp import web
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
import json
import re
import aiohttp
import os
from functools import wraps
from .logging import LOG
from aiocache import cached
from aiocache.serializers import JsonSerializer
from ..api.exceptions import BeaconUnauthorised, BeaconBadRequest, BeaconForbidden, BeaconServerError
from ..conf import OAUTH2_CONFIG
from ..permissions.rems import get_rems_controlled
from ..permissions.ga4gh import get_ga4gh_controlled
from jsonschema import Draft7Validator, validators
from jsonschema.exceptions import ValidationError


async def parse_request_object(request):
    """Parse as JSON Object depending on the request method.

    For POST request parse the body, while for the GET request parse the query parameters.
    """
    if request.method == 'POST':
        LOG.info('Parsed POST request body.')
        return request.method, await request.json()  # we are always expecting JSON

    if request.method == 'GET':
        # GET parameters are returned as strings
        int_params = ['start', 'end', 'endMax', 'endMin', 'startMax', 'startMin']
        items = {k: (int(v) if k in int_params else v) for k, v in request.rel_url.query.items()}
        if 'datasetIds' in items:
            items['datasetIds'] = request.rel_url.query.get('datasetIds').split(',')
        obj = json.dumps(items)
        LOG.info('Parsed GET request parameters.')
        return request.method, json.loads(obj)


# TO DO if required do not set default
def extend_with_default(validator_class):
    """Include default values present in JSON Schema.

    Source: https://python-jsonschema.readthedocs.io/en/latest/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance
    """
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties": set_defaults},
    )


DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


def validate(schema):
    """
    Validate against JSON schema an return something.

    Return a parsed object if there is a POST.
    If there is a get do not return anything just validate.
    """
    def wrapper(func):

        @wraps(func)
        async def wrapped(*args):
            request = args[-1]
            if not isinstance(request, web.Request):
                raise BeaconBadRequest(request, request.host, "invalid request", "This does not seem a valid HTTP Request.")
            try:
                _, obj = await parse_request_object(request)
            except Exception:
                raise BeaconServerError("Could not properly parse the provided Request Body as JSON.")
            try:
                # jsonschema.validate(obj, schema)
                LOG.info('Validate against JSON schema.')
                DefaultValidatingDraft7Validator(schema).validate(obj)
            except ValidationError as e:
                if len(e.path) > 0:
                    LOG.error(f'Bad Request: {e.message} caused by input: {e.instance} in {e.path[0]}')
                    raise BeaconBadRequest(obj, request.host, f"Provided input: '{e.instance}' does not seem correct for field: '{e.path[0]}'")
                else:
                    LOG.error(f'Bad Request: {e.message} caused by input: {e.instance}')
                    raise BeaconBadRequest(obj, request.host, f"Provided input: '{e.instance}' does not seem correct because: '{e.message}'")

            return await func(*args)
        return wrapped
    return wrapper


async def check_bona_fide_status(token, obj, host):
    """Check user details bona_fide_status."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(OAUTH2_CONFIG.bona_fide) as r:
                json_body = await r.json()
                LOG.info('Retrieve a user\'s bona_fide_status.')
                return json_body.get("bona_fide_status", None)
    except Exception:
        raise BeaconServerError("Could not retrieve ELIXIR AAI bona fide status.")


# This can be something that lives longer as it is unlikely to change
@cached(ttl=3600, key="jwk_key", serializer=JsonSerializer())
async def get_key():
    """Get OAuth2 public key and transform it to usable pem key."""
    existing_key = os.environ.get('PUBLIC_KEY', None)
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
    if not re.match('Bearer', scheme):
        raise BeaconUnauthorised(obj, host, "invalid_token", 'Invalid token scheme, Bearer required.')

    if token is None:
        raise BeaconUnauthorised(obj, host, "invalid_token", 'Token cannot be empty.')


def token_auth():
    """Check if token is valid and authenticate.

    Decided against: https://github.com/hzlmn/aiohttp-jwt, as we need to verify
    token issuer and bona_fide_status.
    """
    @web.middleware
    async def token_middleware(request, handler):
        if not isinstance(request, web.Request):
            raise BeaconBadRequest(request, request.host, "invalid request", "This does not seem a valid HTTP Request.")
        if request.path in ['/query'] and 'Authorization' in request.headers:
            _, obj = await parse_request_object(request)
            try:
                # The second item is the token.
                scheme, token = request.headers.get('Authorization').split(' ')
                LOG.info('Auth Token Received.')
            except Exception as e:
                raise BeaconUnauthorised(obj, request.host, "invalid_token", str(e))

            token_scheme_check(token, scheme, obj, request.host)

            key = await get_key()
            issuers = OAUTH2_CONFIG.issuers.split(',')
            aud = os.environ.get('JWT_AUD', OAUTH2_CONFIG.audience)  # defaults to `None` if neither is given
            verify_aud = OAUTH2_CONFIG.verify_aud  # Option to skip verification of `aud` claim
            try:
                decodedData = jwt.decode(token, key, issuer=issuers, audience=aud, options={'verify_aud': verify_aud})
                LOG.info('Auth Token Decoded.')
                LOG.info(f'Identified as {decodedData["sub"]} user by {decodedData["iss"]}.')
                # for now the permissions just reflects that the data can be decoded from token
                # the bona fide status is checked against ELIXIR AAI by default or the URL from config
                # the bona_fide_status is specific to ELIXIR Tokens
                controlled_datasets = set()
                # currently we offer modules for parsing REMS and GA4GH permissions, but multiple claims and providers can be utilised
                # by updating the set, meaning replicating the line below with the permissions function and its associated claim
                # For REMS permissions (ELIXIR Permissions API 1.2)
                controlled_datasets.update(get_rems_controlled(decodedData["permissions_rems"]) if "permissions_rems" in decodedData else {})
                # For GA4GH DURI permissions (ELIXIR Permissions API 2.0)
                controlled_datasets.update(await get_ga4gh_controlled(token,
                                                                      decodedData["ga4gh.userinfo_claims"]) if "ga4gh.userinfo_claims" in decodedData else {})
                all_controlled = list(controlled_datasets) if bool(controlled_datasets) else None
                request["token"] = {"bona_fide_status": True if await check_bona_fide_status(token, obj, request.host) is not None else False,
                                    # permissions key will hold the actual permissions found in the token e.g. REMS permissions
                                    "permissions": all_controlled,
                                    # additional checks can be performed against this authenticated key
                                    # currently if a token is valid that means request is authenticated
                                    "authenticated": True}
                return await handler(request)
            except ExpiredSignatureError as e:
                raise BeaconUnauthorised(obj, request.host, "invalid_token", f'Expired signature: {e}')
            except JWTClaimsError as e:
                raise BeaconForbidden(obj, request.host, f'Token info not corresponding with claim: {e}')
            except JWTError as e:
                raise BeaconUnauthorised(obj, request.host, "invalid_token", f'Invalid authorization token: {e}')
        else:
            request["token"] = {"bona_fide_status": False,
                                "permissions": None,
                                "authenticated": False}
            return await handler(request)
    return token_middleware
