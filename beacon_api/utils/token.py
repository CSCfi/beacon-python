from aiohttp import web
import jwt
import json
from .logging import LOG
from ..api.exceptions import BeaconUnauthorised


def token_auth(key):
    """Check if token if valid and authenticate.

    :type authHeader:
    :param authHeader:  Value of `request.headers.get('Authorization')`.
    :type error_:
    :param error_:  BeaconError object `error_` so it can use it's error handlers.

    :return authenticated: Return a boolean value of `True` or `False` to validate authentication.
    """
    @web.middleware
    async def token_middleware(request, handler):
        assert isinstance(request, web.Request)
        # if request.headers.get('Authorization') is None:
        #     raw_json = await request.read()
        #     obj = json.loads(raw_json.decode('utf-8'))
        #     raise BeaconUnauthorised(obj, "Authorization not set.")
        if request.path in ['/query'] and 'Authorization' in request.headers:
            try:
                # The second item is the token.
                token = request.headers.get('Authorization').split(' ')[1]
                LOG.debug(f' * TOKEN: {token}')
                LOG.debug(f' * KEY: {key}')
                decodeData = jwt.decode(token, key, algorithms=['RS256'])
                LOG.debug(' * Token payload: {}'.format(decodeData))
                request["token"] = True
                return await handler(request)
            except Exception as e:
                # If an exception accures when decoding the token --> the token is invalid or expired, then the error
                # message will be sent in the response.
                raw_json = await request.read()
                obj = json.loads(raw_json.decode('utf-8'))
                raise BeaconUnauthorised(obj, request.host, e)
        else:
            return await handler(request)
    return token_middleware
