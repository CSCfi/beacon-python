from aiohttp import web
import os

from .api.info import beacon_info
from .api.query import query_request_handler
from .conf.config import init_db_pool
from .schemas import load_schema
from .utils.logging import LOG
from .utils.validate import validate, token_auth

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
    LOG.info(' * Get request to beacon end point "/"')
    pool = request.app['pool']
    # TO DO verify match response as in OpenAPI
    response = await beacon_info(request.host, pool)
    return web.json_response(response)


# ----------------------------------------------------------------------------------------------------------------------
#                                         QUERY END POINT OPERATIONS
# ----------------------------------------------------------------------------------------------------------------------
@routes.get('/query')
@validate(load_schema("query"))
async def beacon_get_query(request):
    # TO DO based on token we should check dataset persmissions
    print(request["token"])

    # TO DO move db logic to api module
    # pool = request.app['pool']
    # async with pool.acquire() as connection:
    #     # Open a transaction.
    #     async with connection.transaction():
    #         # Run the query passing the request
    #         result = await connection.fetchrow('SELECT * FROM user')
    #         print(result)
    return web.Response(text="nothing")


@routes.post('/query')
@validate(load_schema("query"))
async def beacon_post_query(request):
    # LOG.info(request.method)
    # TO DO based on token we should check dataset persmissions
    # print(request["token"])
    # print(await request.read())
    response = query_request_handler(request.method, await request.json(), None, request.host)
    return web.json_response(response)


async def create_db_pool(app):
    # TO DO check if table and Databse exist
    # and maybe exit gracefully or at lease wait for a bit
    app['pool'] = await init_db_pool()


async def close_db_pool(app):
    await app['pool'].close()


def init():
    """Initialise server."""
    # TO DO see if there is a better way to get the Public Key
    key = os.environ.get('PUBLIC_KEY', '')  # .replace(r'\n', '\n')
    beacon = web.Application(middlewares=[token_auth(key)])
    beacon.router.add_routes(routes)
    # Create a database connection pool
    beacon.on_startup.append(create_db_pool)
    beacon.on_cleanup.append(close_db_pool)
    return beacon


def main():
    """Run the beacon API.

    At start also initialize a PostgreSQL connection pool.
    """
    # TO DO make it HTTPS and request certificate
    web.run_app(init(), host=os.environ.get('HOST', '0.0.0.0'),
                port=os.environ.get('PORT', '8080'),
                shutdown_timeout=0, ssl_context=None)


if __name__ == '__main__':
    main()
