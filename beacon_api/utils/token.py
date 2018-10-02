from aiohttp import web
import os
import jwt
from .logging import LOG
from ..api.exceptions import BeaconUnauthorised


def token_auth():
    """Check if token if valid and authenticate.

    :type authHeader:
    :param authHeader:  Value of `request.headers.get('Authorization')`.
    :type error_:
    :param error_:  BeaconError object `error_` so it can use it's error handlers.

    :return authenticated: Return a boolean value of `True` or `False` to validate authentication.
    """
    @web.middleware
    async def token_middleware(request, handler):
        authenticated = False
        try:
            # The second item is the token.
            token = authHeader.split(' ')[1]
            key = os.environ.get('PUBLIC_KEY').replace(r'\n', '\n')
            LOG.debug(' * TOKEN: {}'.format(token))
            LOG.debug(' * KEY: {}'.format(key))
            decodeData = jwt.decode(token, key, algorithms=['RS256'])
            authenticated = True
            LOG.debug(' * Token payload: {}'.format(decodeData))
        except Exception as e:
            # If an exception accures when decoding the token --> the token is invalid or expired, then the error
            # message will be sent in the response.
            LOG.warning(' * * * 401 ERROR MESSAGE: Authorization failed, token invalid.')
            raise BeaconUnauthorised(request, e)
        finally:
            return authenticated
    return token_middleware
