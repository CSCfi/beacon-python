"""Mock OAUTH2 aiohttp.web server."""

from aiohttp import web

TOKEN_EMPTY = "eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJyZXF1ZXN0ZXJAZWx\
peGlyLWV1cm9wZS5vcmciLCJpc3MiOiJodHRwOi8vc29tZWJvZHkuY29tIiwiZXhwIjo5OTk5OTk5OTk5\
OSwiaWF0IjoxNTQ3Nzk0NjU1LCJqdGkiOiI2YWQ3YWE0Mi0zZTljLTQ4MzMtYmQxNi03NjVjYjgwYzIxM\
DIifQ.HPr3_N_4E-w_sIWS0kO7b-1VGVBuwQpgQoA2DRWj86YRt11JM_lpG58NrZwUOKXIOn4yV-HnrHe\
4pXn07bEZ_EgcqBsNnVHE51iiKZUS3v3gkBrLJ5miogjCdxz-wNnIm45ceSIW1PSRTkKDJpwmzigfvP_l\
GHpxwmUKAmRwFnw"


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
    """Mock an authentication to ELIXIR AAI for GA4GH claims."""
    if request.headers.get('Authorization').split(' ')[1] == TOKEN_EMPTY:
        data = {}
    else:
        data = {
            "ga4gh": {
                "AcceptedTermsAndPolicies": [
                    {
                        "value": "https://doi.org/10.1038/s41431-018-0219-y",
                        "source": "https://ga4gh.org/duri/no_org",
                        "by": "self",
                        "asserted": 1539069213,
                        "expires": 9999999999
                    }
                ],
                "ResearcherStatus": [
                    {
                        "value": "https://doi.org/10.1038/s41431-018-0219-y",
                        "source": "https://ga4gh.org/duri/no_org",
                        "by": "peer",
                        "asserted": 1539017776,
                        "expires": 9999999999
                    }
                ],
                "ControlledAccessGrants": [
                    {
                        "value": "https://www.ebi.ac.uk/ega/urn:hg:1000genome",
                        "source": "https://ga4gh.org/duri/no_org",
                        "by": "dac",
                        "asserted": 1559893314,
                        "expires": 9999999999
                    },
                    {
                        "value": "https://www.ebi.ac.uk/ega/urn:hg:1000genome:controlled",
                        "source": "https://ga4gh.org/duri/no_org",
                        "by": "dac",
                        "asserted": 1559897355,
                        "expires": 9999999999
                    },
                    {
                        "value": "https://www.ebi.ac.uk/ega/urn:hg:1000genome:controlled1",
                        "source": "https://ga4gh.org/duri/no_org",
                        "by": "dac",
                        "asserted": 1560169441,
                        "expires": 9999999999
                    }
                ]
            }
        }
    return web.json_response(data)


def init():
    """Start server."""
    app = web.Application()
    app.router.add_get('/jwk', jwk)
    app.router.add_get('/userinfo', userinfo)
    return app


if __name__ == '__main__':
    web.run_app(init(), port=8000)
