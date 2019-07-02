"""Mock OAUTH2 aiohttp.web server."""

from aiohttp import web
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from authlib.jose import jwt, jwk


def generate_token():
    """Generate RSA Key pair to be used to sign token and the JWT Token itself."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())
    public_key = private_key.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                                    encryption_algorithm=serialization.NoEncryption())
    # we set no `exp` and other claims as they are optional in a real scenario these should be set
    # See available claims here: https://www.iana.org/assignments/jwt/jwt.xhtml
    # the important claim is the "authorities"
    header = {
        "jku": "http://mockauth:8000/jwk",
        "kid": "rsa1",
        "alg": "RS256",
        "typ": "JWT"
    }
    dataset_payload = {
        "sub": "requester@elixir-europe.org",
        "aud": ["aud2", "aud3"],
        "azp": "azp",
        "scope": "openid ga4gh",
        "iss": "http://test.csc.fi",
        "exp": 9999999999,
        "iat": 1561621913,
        "jti": "6ad7aa42-3e9c-4833-bd16-765cb80c2102",
        "ga4gh_userinfo_claims": [
            "ga4gh.AffiliationAndRole",
            "ga4gh.ControlledAccessGrants",
            "ga4gh.AcceptedTermsAndPolicies",
            "ga4gh.ResearcherStatus"
        ]
    }
    empty_payload = {
        "sub": "requester@elixir-europe.org",
        "iss": "http://test.csc.fi",
        "exp": 99999999999,
        "iat": 1547794655,
        "jti": "6ad7aa42-3e9c-4833-bd16-765cb80c2102"
    }
    public_jwk = jwk.dumps(public_key, kty='RSA')
    private_jwk = jwk.dumps(pem, kty='RSA')
    dataset_encoded = jwt.encode(header, dataset_payload, private_jwk).decode('utf-8')
    empty_encoded = jwt.encode(header, empty_payload, private_jwk).decode('utf-8')
    return (public_jwk, dataset_encoded, empty_encoded)


DATA = generate_token()


async def jwk_response(request):
    """Mock JSON Web Key server."""
    data = [DATA[0]]
    data[0]['kid'] = 'rsa1'
    return web.json_response(data)


async def tokens_response(request):
    """Serve generated tokens."""
    data = [DATA[1], DATA[2]]
    return web.json_response(data)


async def userinfo(request):
    """Mock an authentication to ELIXIR AAI for GA4GH claims."""
    if request.headers.get('Authorization').split(' ')[1] == DATA[2]:
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
                    }
                ]
            }
        }
    return web.json_response(data)


def init():
    """Start server."""
    app = web.Application()
    app.router.add_get('/jwk', jwk_response)
    app.router.add_get('/tokens', tokens_response)
    app.router.add_get('/userinfo', userinfo)
    return app


if __name__ == '__main__':
    web.run_app(init(), port=8000)
