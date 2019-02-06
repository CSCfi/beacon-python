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
# Draft7Validator should be kept an eye on as this might change
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
            assert isinstance(request, web.Request)
            try:
                _, obj = await parse_request_object(request)
            except Exception:
                raise BeaconServerError("Could not properly parse the provided Request Body as JSON.")
            try:
                # jsonschema.validate(obj, schema)
                LOG.info('Validate against JSON schema.')
                DefaultValidatingDraft7Validator(schema).validate(obj)
            except ValidationError as e:
                raise BeaconBadRequest(obj, request.host, e.message)

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
                # This can be a single key or a set of JWK
                return await r.json()
    except Exception:
        raise BeaconServerError("Could not retrieve OAuth2 public key.")


def token_auth():
    """Check if token if valid and authenticate.

    Decided against: https://github.com/hzlmn/aiohttp-jwt, as we need to verify
    token issuer and bona_fide_status.
    """
    @web.middleware
    async def token_middleware(request, handler):
        assert isinstance(request, web.Request)
        if request.path in ['/query'] and 'Authorization' in request.headers:
            _, obj = await parse_request_object(request)
            try:
                # The second item is the token.
                scheme, token = request.headers.get('Authorization').split(' ')
                LOG.info('Auth Token Received.')
            except Exception as e:
                raise BeaconUnauthorised(obj, request.host, str(e))

            if not re.match('Bearer', scheme):
                raise BeaconUnauthorised(obj, request.host, 'Invalid token scheme.')

            assert token is not None, BeaconUnauthorised(obj, request.host, f'Token cannot be empty.')
            key = await get_key()
            issuers = OAUTH2_CONFIG.issuers.split(',')
            try:
                decodedData = jwt.decode(token, key, issuer=issuers)
                LOG.info('Auth Token Decoded.')
                LOG.info(f'Identified as {decodedData["sub"]} user by {decodedData["iss"]}.')
                # for now the permissions just reflect that the data can be decoded from token
                # the bona fide status is checked against ELIXIR AAI
                # the bona_fide_status is specific to ELIXIR Tokens
                # permissions key will hold the actual permissions found in the token e.g. REMS permissions
                controlled_datasets = set()
                # currently we parse only REMS, but multiple claims and providers can be utilised
                # by updating the set, replicating the line below with the permissions function and its associated claim
                controlled_datasets.update(get_rems_controlled(decodedData["permissions_rems"]) if "permissions_rems" in decodedData else {})
                all_controlled = list(controlled_datasets) if bool(controlled_datasets) else None
                request["token"] = {"bona_fide_status": True if await check_bona_fide_status(token, obj, request.host) else False,
                                    "permissions": all_controlled,
                                    "authenticated": True}
                return await handler(request)
            except ExpiredSignatureError as e:
                raise BeaconUnauthorised(obj, request.host, f'Expired signature: {e}')
            except JWTClaimsError as e:
                raise BeaconForbidden(obj, request.host, f'Token info not corresponding with claim: {e}')
            except JWTError as e:
                raise BeaconUnauthorised(obj, request.host, f'Invalid authorization token: {e}')
        else:
            request["token"] = {"bona_fide_status": False,
                                "permissions": None,
                                "authenticated": False}
            return await handler(request)
    return token_middleware
