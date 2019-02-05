"""Mock OAUTH2 aiohttp.web server."""

from aiohttp import web


async def jwk(request):
    """Mock JSON Web Key server."""
    data = [{"kty": "RSA",
             "n": "3ZWrUY0Y6IKN1qI4BhxR2C7oHVFgGPYkd38uGq1jQNSqEvJFcN93CYm16_G78FAFKWqws\
             Jb3Wx-nbxDn6LtP4AhULB1H0K0g7_jLklDAHvI8yhOKlvoyvsUFPWtNxlJyh5JJXvkNKV_4Oo12e69f8QCuQ6NpEPl-cSvXIqUYBCs",
             "e": "AQAB",
             "alg": "RS256",
             "kid": "rsa1"}]
    return web.json_response(data)


async def userinfo(request):
    """Mock an authentication to ELIXIR AAI bona_fide."""
    data = {'bona_fide_status': "yes we can"}
    return web.json_response(data)


def init():
    """Start server."""
    app = web.Application()
    app.router.add_get('/jwk', jwk)
    app.router.add_get('/userinfo', userinfo)
    return app


if __name__ == '__main__':
    web.run_app(init(), port=8000)
