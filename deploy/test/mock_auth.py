"""Mock OAUTH2 aiohttp.web server."""

from aiohttp import web
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from authlib.jose import jwt, jwk
from typing import Tuple


def generate_token() -> Tuple:
    """Generate RSA Key pair to be used to sign token and the JWT Token itself."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption()
    )
    # we set no `exp` and other claims as they are optional in a real scenario these should be set
    # See available claims here: https://www.iana.org/assignments/jwt/jwt.xhtml
    # the important claim is the "authorities"
    header = {"jku": "http://mockauth:8000/jwk", "kid": "rsa1", "alg": "RS256", "typ": "JWT"}
    dataset_payload = {
        "sub": "requester@elixir-europe.org",
        "aud": ["aud2", "aud3"],
        "azp": "azp",
        "scope": "openid ga4gh_passport_v1",
        "iss": "http://test.csc.fi",
        "exp": 9999999999,
        "iat": 1561621913,
        "jti": "6ad7aa42-3e9c-4833-bd16-765cb80c2102",
    }
    empty_payload = {
        "sub": "requester@elixir-europe.org",
        "iss": "http://test.csc.fi",
        "exp": 99999999999,
        "iat": 1547794655,
        "jti": "6ad7aa42-3e9c-4833-bd16-765cb80c2102",
    }
    # Craft 4 passports, 2 for bona fide status and 2 for dataset permissions
    # passport for bona fide: terms
    passport_terms = {
        "iss": "http://test.csc.fi",
        "sub": "requester@elixir-europe.org",
        "ga4gh_visa_v1": {
            "type": "AcceptedTermsAndPolicies",
            "value": "https://doi.org/10.1038/s41431-018-0219-y",
            "source": "https://ga4gh.org/duri/no_org",
            "by": "dac",
            "asserted": 1568699331,
        },
        "iat": 1571144438,
        "exp": 99999999999,
        "jti": "bed0aff9-29b1-452c-b776-a6f2200b6db1",
    }
    # passport for bona fide: status
    passport_status = {
        "iss": "http://test.csc.fi",
        "sub": "requester@elixir-europe.org",
        "ga4gh_visa_v1": {
            "type": "ResearcherStatus",
            "value": "https://doi.org/10.1038/s41431-018-0219-y",
            "source": "https://ga4gh.org/duri/no_org",
            "by": "peer",
            "asserted": 1568699331,
        },
        "iat": 1571144438,
        "exp": 99999999999,
        "jti": "722ddde1-617d-4651-992d-f0fdde77bf29",
    }
    # passport for dataset permissions 1
    passport_dataset1 = {
        "iss": "http://test.csc.fi",
        "sub": "requester@elixir-europe.org",
        "ga4gh_visa_v1": {
            "type": "ControlledAccessGrants",
            "value": "https://www.ebi.ac.uk/ega/urn:hg:1000genome:controlled",
            "source": "https://ga4gh.org/duri/no_org",
            "by": "self",
            "asserted": 1568699331,
        },
        "iat": 1571144438,
        "exp": 99999999999,
        "jti": "d1d7b521-bd6b-433d-b2d5-3d874aab9d55",
    }
    # passport for dataset permissions 2
    passport_dataset2 = {
        "iss": "http://test.csc.fi",
        "sub": "requester@elixir-europe.org",
        "ga4gh_visa_v1": {
            "type": "ControlledAccessGrants",
            "value": "https://www.ebi.ac.uk/ega/urn:hg:1000genome:controlled1",
            "source": "https://ga4gh.org/duri/no_org",
            "by": "dac",
            "asserted": 1568699331,
        },
        "iat": 1571144438,
        "exp": 99999999999,
        "jti": "9fa600d6-4148-47c1-b708-36c4ba2e980e",
    }
    public_jwk = jwk.dumps(public_key, kty="RSA")
    private_jwk = jwk.dumps(pem, kty="RSA")
    dataset_encoded = jwt.encode(header, dataset_payload, private_jwk).decode("utf-8")
    empty_encoded = jwt.encode(header, empty_payload, private_jwk).decode("utf-8")
    passport_terms_encoded = jwt.encode(header, passport_terms, private_jwk).decode("utf-8")
    passport_status_encoded = jwt.encode(header, passport_status, private_jwk).decode("utf-8")
    passport_dataset1_encoded = jwt.encode(header, passport_dataset1, private_jwk).decode("utf-8")
    passport_dataset2_encoded = jwt.encode(header, passport_dataset2, private_jwk).decode("utf-8")
    return (public_jwk, dataset_encoded, empty_encoded, passport_terms_encoded, passport_status_encoded, passport_dataset1_encoded, passport_dataset2_encoded)


DATA = generate_token()


async def jwk_response(request: web.Request) -> web.Response:
    """Mock JSON Web Key server."""
    keys = [DATA[0]]
    keys[0]["kid"] = "rsa1"
    data = {"keys": keys}
    return web.json_response(data)


async def tokens_response(request: web.Request) -> web.Response:
    """Serve generated tokens."""
    data = [DATA[1], DATA[2]]
    return web.json_response(data)


async def userinfo(request: web.Request) -> web.Response:
    """Mock an authentication to ELIXIR AAI for GA4GH claims."""
    if request.headers.get("Authorization").split(" ")[1] == DATA[2]:
        data = {}
    else:
        data = {"ga4gh_passport_v1": [DATA[3], DATA[4], DATA[5], DATA[6]]}
    return web.json_response(data)


def init() -> web.Application:
    """Start server."""
    app = web.Application()
    app.router.add_get("/jwk", jwk_response)
    app.router.add_get("/tokens", tokens_response)
    app.router.add_get("/userinfo", userinfo)
    return app


if __name__ == "__main__":
    web.run_app(init(), port=8000)
