"""Beacon API Web Server.

Server was designed with aync/await mindset and with at aim at performance (TBD).
"""

from aiohttp import web
import os
import sys
import aiohttp_cors

from .api.info import beacon_info
from .api.query import query_request_handler
from .conf.config import init_db_pool
from .schemas import load_schema
from .utils.logging import LOG
from .utils.validate import validate, token_auth, parse_request_object

routes = web.RouteTableDef()


# ----------------------------------------------------------------------------------------------------------------------
#                                         INFO END POINT OPERATIONS
# ----------------------------------------------------------------------------------------------------------------------
@routes.get('/', name='info')
async def beacon_get(request):
    """
    Use the HTTP protocol 'GET' to return a Json object of all the necessary info on the beacon and the API.

    It uses the '/' path and only serves an information giver.

    :type beacon: Dict
    :return beacon: The method returns an example Beacon characteristic to beacon info endpoint.
    """
    LOG.info('GET request to the info endpoint "/".')
    db_pool = request.app['pool']
    response = await beacon_info(request.host, db_pool)
    return web.json_response(response)


# ----------------------------------------------------------------------------------------------------------------------
#                                         QUERY END POINT OPERATIONS
# ----------------------------------------------------------------------------------------------------------------------
# These could be put under a @route.view('/query')
@routes.get('/query')
@validate(load_schema("query"))
async def beacon_get_query(request):
    """Find datasets using GET endpoint."""
    method, processed_request = await parse_request_object(request)
    params = request.app['pool'], method, processed_request, request["token"], request.host
    response = await query_request_handler(params)
    return web.json_response(response)


@routes.post('/query')
@validate(load_schema("query"))
async def beacon_post_query(request):
    """Find datasets using POST endpoint."""
    method, processed_request = await parse_request_object(request)
    params = request.app['pool'], method, processed_request, request["token"], request.host
    response = await query_request_handler(params)
    return web.json_response(response)


async def initialize(app):
    """Spin up DB a connection pool with the HTTP server."""
    # TO DO check if table and Database exist
    # and maybe exit gracefully or at lease wait for a bit
    LOG.debug('Create PostgreSQL connection pool.')
    app['pool'] = await init_db_pool()


async def destroy(app):
    """Upon server close, close the DB connection pool."""
    await app['pool'].close()


def set_cors(server):
    """Set CORS rules."""
    # Configure CORS settings
    cors = aiohttp_cors.setup(server, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    # Apply CORS to endpoints
    for route in list(server.router.routes()):
        cors.add(route)


def init():
    """Initialise server."""
    beacon = web.Application(middlewares=[token_auth()])
    beacon.router.add_routes(routes)
    set_cors(beacon)
    beacon.on_startup.append(initialize)
    beacon.on_cleanup.append(destroy)
    return beacon


def main():
    """Run the beacon API.

    At start also initialize a PostgreSQL connection pool.
    """
    # TO DO make it HTTPS and request certificate
    # sslcontext.load_cert_chain(ssl_certfile, ssl_keyfile)
    # sslcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # sslcontext.check_hostname = False
    web.run_app(init(), host=os.environ.get('HOST', '0.0.0.0'),
                port=os.environ.get('PORT', '5050'),
                shutdown_timeout=0, ssl_context=None)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), "beacon-python requires python3.6"
    main()
