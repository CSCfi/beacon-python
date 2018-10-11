"""JSON Request/Response Validation and Token authentication."""

from aiohttp import web
import jwt
import json
import re
import aiohttp
import base64
import struct
import os
from functools import wraps
from .logging import LOG
from ..api.exceptions import BeaconUnauthorised, BeaconBadRequest, BeaconForbidden, BeaconServerError
# Draft7Validator should be kept an eye on as this might change
from jsonschema import Draft7Validator, validators
from jsonschema.exceptions import ValidationError
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


async def parse_request_object(request):
    """Parse as JSON Object depending on the request method.

    For POST request parse the body, while for the GET request parse the query parameters.
    """
    if request.method == 'POST':
        return request.method, await request.json()  # we are always expecting JSON

    if request.method == 'GET':
        # GET parameters are returned as strings
        int_params = ['start', 'end', 'endMax', 'endMin', 'startMax', 'startMin']
        items = {k: (int(v) if k in int_params else v) for k, v in request.rel_url.query.items()}
        obj = json.dumps(items)

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
                # TO DO verify match response as in OpenAPI
                raise BeaconServerError("Could not properly parse the provided Request Body as JSON.")
            try:
                # jsonschema.validate(obj, schema)
                DefaultValidatingDraft7Validator(schema).validate(obj)
            except ValidationError as e:
                # TO DO verify match response as in OpenAPI
                raise BeaconBadRequest(obj, request.host, e.message)

            return await func(*args)
        return wrapped
    return wrapper


async def check_bona_fide_status(token):
    """Check user details bona_fide_status."""
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get("https://login.elixir-czech.org/oidc/userinfo") as r:
            json_body = await r.json()
            return json_body.get("bona_fide_status", None)


def base64_to_long(data):
    """Convert JSON Web Key to armored key."""
    # urlsafe_b64decode will happily convert b64encoded data
    _d = base64.urlsafe_b64decode(bytes(data.encode("ascii")) + b'==')
    unpacked = struct.unpack('%sB' % len(_d), _d)
    converted = int(''.join(["%02x" % byte for byte in unpacked]), 16)
    return converted


async def get_key():
    """Get Elixir public key and transform it to usable pem key."""
    existing_key = os.environ.get('PUBLIC_KEY', None)
    if existing_key:
        return existing_key
    async with aiohttp.ClientSession() as session:
        async with session.get("https://login.elixir-czech.org/oidc/jwk") as r:
            jwk = await r.json()
            exponent = base64_to_long(jwk['keys'][0]['e'])
            modulus = base64_to_long(jwk['keys'][0]['n'])
            numbers = RSAPublicNumbers(exponent, modulus)
            public_key = numbers.public_key(backend=default_backend())
            pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                          format=serialization.PublicFormat.SubjectPublicKeyInfo)
            return pem.decode('utf-8')


def token_auth():
    """Check if token if valid and authenticate.

    Decided not to use: https://github.com/hzlmn/aiohttp-jwt, as we need to verify
    ELIXIR AAI issuer and bona_fide_status.
    """
    @web.middleware
    async def token_middleware(request, handler):
        assert isinstance(request, web.Request)
        if request.path in ['/query'] and 'Authorization' in request.headers:
            try:
                # The second item is the token.
                scheme, token = request.headers.get('Authorization').split(' ')
                LOG.info('Auth Token Received.')
            except Exception as e:
                _, obj = await parse_request_object(request)
                raise BeaconUnauthorised(obj, request.host, str(e))

            if not re.match('Bearer', scheme):
                _, obj = await parse_request_object(request)
                raise BeaconUnauthorised(obj, request.host, 'Invalid token scheme.')

            if token is not None:
                key = await get_key()
                try:
                    decodedData = jwt.decode(token, key, algorithms=['RS256'])
                    LOG.info('Auth Token Decoded.')
                except jwt.InvalidTokenError as e:
                    _, obj = await parse_request_object(request)
                    raise BeaconUnauthorised(obj, request.host, f'Invalid authorization token: {e}')

                # Validate the issuer is Elixir AAI
                if decodedData['iss'] in ["https://login.elixir-czech.org/oidc/"] and decodedData['sub'].endswith("@elixir-europe.org"):
                    LOG.info('Identified as Elixir AAI user.')
                    # for now the permissions just reflect the decoded data
                    # the bona fide status for now is set to True
                    if await check_bona_fide_status(token):
                        request["token"] = {"bona_fide_status": True}
                        return await handler(request)
                    else:
                        request["token"] = {"bona_fide_status": False}
                        return await handler(request)
                else:
                    _, obj = await parse_request_object(request)
                    raise BeaconForbidden(obj, request.host, 'Token is not validated by an Elixir AAI authorized issuer.')
        else:
            request["token"] = {"bona_fide_status": False}
            return await handler(request)
    return token_middleware
