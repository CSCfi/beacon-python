import unittest
from aiohttp.test_utils import AioHTTPTestCase
from beacon_api.app import init, initialize
import asyncpg
import json
from authlib.jose import jwt
import os
from test.support.os_helper import EnvironmentVarGuard
from aiocache import caches


PARAMS = {"assemblyId": "GRCh38", "referenceName": "1", "start": 10000, "referenceBases": "A", "alternateBases": "T"}


def generate_token(issuer):
    """Mock ELIXIR AAI token."""
    pem = {
        "kty": "oct",
        "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037",
        "use": "sig",
        "alg": "HS256",
        "k": "hJtXIZ2uSN5kbQfbtTNWbpdmhkV8FJG-Onbc6mxCcYg",
    }
    header = {"jku": "http://test.csc.fi/jwk", "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037", "alg": "HS256"}
    payload = {"iss": issuer, "aud": "audience", "exp": 9999999999, "sub": "smth@smth.org"}
    token = jwt.encode(header, payload, pem).decode("utf-8")
    return token, pem


def generate_bad_token():
    """Mock AAI token."""
    pem = {
        "kty": "oct",
        "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037",
        "use": "sig",
        "alg": "HS256",
        "k": "hJtXIZ2uSN5kbQfbtTNWbpdmhkV8FJG-Onbc6mxCcYg",
    }
    header = {"jku": "http://test.csc.fi/jwk", "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037", "alg": "HS256"}
    payload = {"iss": "bad_issuer", "aud": "audience", "exp": 0, "sub": "smth@elixir-europe.org"}
    token = jwt.encode(header, payload, pem).decode("utf-8")
    return token, pem


async def create_db_mock(app):
    """Mock the db connection pool."""
    app["pool"] = unittest.mock.Mock(asyncpg.create_pool())
    return app


async def mock_parse_request_object(request):
    """Mock parse request object."""
    return "GET", json.dumps(PARAMS)


class AppTestCase(AioHTTPTestCase):
    """Test for Web app.

    Testing web app endpoints.
    """

    @unittest.mock.patch("beacon_api.app.initialize", side_effect=create_db_mock)
    async def get_application(self, pool_mock):
        """Retrieve web Application for test."""
        token, public_key = generate_token("http://test.csc.fi")
        self.bad_token, _ = generate_bad_token()
        self.env = EnvironmentVarGuard()
        self.env.set("PUBLIC_KEY", json.dumps(public_key))
        self.env.set("TOKEN", token)
        return await init()

    async def tearDownAsync(self):
        """Finish up tests."""
        self.env.unset("PUBLIC_KEY")
        self.env.unset("TOKEN")
        await caches.get("default").delete("jwk_key")

    async def test_beacon_info(self):
        """Test the Beacon info endpoint.

        The status should always be 200.
        """
        with unittest.mock.patch("beacon_api.app.beacon_info", return_value={"id": "value"}):
            resp = await self.client.request("GET", "/")
        self.assertEqual(200, resp.status)

    async def test_ga4gh_info(self):
        """Test the GA4GH Discovery info endpoint.

        The status should always be 200.
        """
        with unittest.mock.patch("beacon_api.app.ga4gh_info", return_value={"id": "value"}):
            resp = await self.client.request("GET", "/service-info")
        self.assertEqual(200, resp.status)

    async def test_post_info(self):
        """Test the info endpoint with POST.

        The status should always be 405.
        """
        resp = await self.client.request("POST", "/")
        self.assertEqual(405, resp.status)

    async def test_post_service_info(self):
        """Test the service-info endpoint with POST.

        The status should always be 405.
        """
        resp = await self.client.request("POST", "/service-info")
        self.assertEqual(405, resp.status)

    async def test_empty_get_query(self):
        """Test empty GET query endpoint."""
        resp = await self.client.request("GET", "/query")
        self.assertEqual(400, resp.status)

    async def test_empty_post_query(self):
        """Test empty POST query endpoint."""
        resp = await self.client.request("POST", "/query", data=json.dumps({}))
        self.assertEqual(400, resp.status)

    async def test_bad_start_post_query(self):
        """Test bad start combination POST query endpoint."""
        bad_start = {
            "referenceName": "MT",
            "endMin": 10,
            "end": 20,
            "startMin": 10,
            "startMax": 10,
            "referenceBases": "T",
            "variantType": "MNP",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
        }
        resp = await self.client.request("POST", "/query", data=json.dumps(bad_start))
        self.assertEqual(400, resp.status)

    async def test_bad_start2_post_query(self):
        """Test bad start combination 2 POST query endpoint."""
        bad_start = {
            "referenceName": "MT",
            "start": 10,
            "end": 20,
            "startMin": 10,
            "startMax": 10,
            "referenceBases": "T",
            "variantType": "MNP",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
        }
        resp = await self.client.request("POST", "/query", data=json.dumps(bad_start))
        self.assertEqual(400, resp.status)

    async def test_bad_startend_post_query(self):
        """Test end smaller than start POST query endpoint."""
        bad_start = {
            "referenceName": "MT",
            "start": 10,
            "end": 9,
            "referenceBases": "T",
            "variantType": "MNP",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
        }
        resp = await self.client.request("POST", "/query", data=json.dumps(bad_start))
        self.assertEqual(400, resp.status)

    async def test_bad_startminmax_post_query(self):
        """Test start min greater than start Max POST query endpoint."""
        bad_start = {
            "referenceName": "MT",
            "startMin": 10,
            "startMax": 9,
            "referenceBases": "T",
            "variantType": "MNP",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
        }
        resp = await self.client.request("POST", "/query", data=json.dumps(bad_start))
        self.assertEqual(400, resp.status)

    async def test_bad_endminmax_post_query(self):
        """Test end min greater than start Max POST query endpoint."""
        bad_start = {
            "referenceName": "MT",
            "endMin": 10,
            "endMax": 9,
            "referenceBases": "T",
            "variantType": "MNP",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
        }
        resp = await self.client.request("POST", "/query", data=json.dumps(bad_start))
        self.assertEqual(400, resp.status)

    @unittest.mock.patch("beacon_api.app.parse_request_object", side_effect=mock_parse_request_object)
    @unittest.mock.patch("beacon_api.app.query_request_handler")
    async def test_good_start_post_query(self, mock_handler, mock_object):
        """Test good start combination POST query endpoint."""
        good_start = {
            "referenceName": "MT",
            "start": 10,
            "referenceBases": "T",
            "variantType": "MNP",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
        }
        mock_handler.side_effect = json.dumps(good_start)
        resp = await self.client.request("POST", "/query", data=json.dumps(good_start))
        self.assertEqual(200, resp.status)

    @unittest.mock.patch("beacon_api.app.parse_request_object", side_effect=mock_parse_request_object)
    @unittest.mock.patch("beacon_api.app.query_request_handler")
    async def test_good_start2_post_query(self, mock_handler, mock_object):
        """Test good start combination 2 POST query endpoint."""
        good_start = {
            "referenceName": "MT",
            "start": 10,
            "end": 20,
            "referenceBases": "T",
            "variantType": "MNP",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
        }
        mock_handler.side_effect = json.dumps(good_start)
        resp = await self.client.request("POST", "/query", data=json.dumps(good_start))
        self.assertEqual(200, resp.status)

    @unittest.mock.patch("beacon_api.app.parse_request_object", side_effect=mock_parse_request_object)
    @unittest.mock.patch("beacon_api.app.query_request_handler")
    async def test_good_start3_post_query(self, mock_handler, mock_object):
        """Test good start combination 3 POST query endpoint."""
        good_start = {
            "referenceName": "MT",
            "startMin": 10,
            "startMax": 20,
            "referenceBases": "T",
            "variantType": "MNP",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
        }
        mock_handler.side_effect = json.dumps(good_start)
        resp = await self.client.request("POST", "/query", data=json.dumps(good_start))
        self.assertEqual(200, resp.status)

    async def test_unauthorized_no_token_post_query(self):
        """Test unauthorized POST query endpoint, with no token."""
        resp = await self.client.request("POST", "/query", data=json.dumps(PARAMS), headers={"Authorization": "Bearer"})
        self.assertEqual(401, resp.status)

    async def test_unauthorized_token_post_query(self):
        """Test unauthorized POST query endpoint, bad token."""
        resp = await self.client.request("POST", "/query", data=json.dumps(PARAMS), headers={"Authorization": f"Bearer {self.bad_token}"})
        self.assertEqual(403, resp.status)

    async def test_invalid_scheme_get_query(self):
        """Test unauthorized GET query endpoint, invalid scheme."""
        params = "?assemblyId=GRCh38&referenceName=1&start=10000&referenceBases=A&alternateBases=T&datasetIds=dataset1"
        resp = await self.client.request("GET", f"/query{params}", headers={"Authorization": "SMTH x"})
        self.assertEqual(401, resp.status)

    @unittest.mock.patch("beacon_api.app.parse_request_object", side_effect=mock_parse_request_object)
    @unittest.mock.patch("beacon_api.app.query_request_handler", side_effect=json.dumps(PARAMS))
    async def test_valid_token_get_query(self, mock_handler, mock_object):
        """Test valid token GET query endpoint."""
        token = os.environ.get("TOKEN")
        resp = await self.client.request("POST", "/query", data=json.dumps(PARAMS), headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(200, resp.status)

    async def test_bad_json_post_query(self):
        """Test bad json POST query endpoint."""
        resp = await self.client.request("POST", "/query", data="")
        self.assertEqual(500, resp.status)

    @unittest.mock.patch("beacon_api.app.parse_request_object", side_effect=mock_parse_request_object)
    @unittest.mock.patch("beacon_api.app.query_request_handler", side_effect=json.dumps(PARAMS))
    async def test_valid_get_query(self, mock_handler, mock_object):
        """Test valid GET query endpoint."""
        params = "?assemblyId=GRCh38&referenceName=1&start=10000&referenceBases=A&alternateBases=T"
        with unittest.mock.patch("beacon_api.app.initialize", side_effect=create_db_mock):
            resp = await self.client.request("GET", f"/query{params}")
        self.assertEqual(200, resp.status)

    @unittest.mock.patch("beacon_api.app.parse_request_object", side_effect=mock_parse_request_object)
    @unittest.mock.patch("beacon_api.app.query_request_handler", side_effect=json.dumps(PARAMS))
    async def test_valid_post_query(self, mock_handler, mock_object):
        """Test valid POST query endpoint."""
        resp = await self.client.request("POST", "/query", data=json.dumps(PARAMS))
        self.assertEqual(200, resp.status)


class AppTestCaseForbidden(AioHTTPTestCase):
    """Test for Web app 403.

    Testing web app for wrong issuer.
    """

    async def tearDownAsync(self):
        """Finish up tests."""
        self.env.unset("PUBLIC_KEY")
        self.env.unset("TOKEN")
        await caches.get("default").delete("jwk_key")

    @unittest.mock.patch("beacon_api.app.initialize", side_effect=create_db_mock)
    async def get_application(self, pool_mock):
        """Retrieve web Application for test."""
        token, public_key = generate_token("something")
        self.env = EnvironmentVarGuard()
        self.env.set("PUBLIC_KEY", json.dumps(public_key))
        self.env.set("TOKEN", token)
        return await init()

    @unittest.mock.patch("beacon_api.app.parse_request_object", side_effect=mock_parse_request_object)
    @unittest.mock.patch("beacon_api.app.query_request_handler", side_effect=json.dumps(PARAMS))
    async def test_forbidden_token_get_query(self, mock_handler, mock_object):
        """Test forbidden GET query endpoint, invalid scheme."""
        token = os.environ.get("TOKEN")
        resp = await self.client.request("POST", "/query", data=json.dumps(PARAMS), headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(403, resp.status)


class TestBasicFunctionsApp(unittest.IsolatedAsyncioTestCase):
    """Test App Base.

    Testing basic functions from web app.
    """

    async def test_servinit(self):
        """Test server initialization function execution."""
        # Don't really need much testing here, if the server initialization
        # executes to the end all is fine.
        app = await init()
        self.assertTrue(app is not None)

    @unittest.mock.patch("beacon_api.app.set_cors")
    async def test_initialize(self, mock_cors):
        """Test create db pool, should just return the result of init_db_pool.

        We will mock the init_db_pool, thus we assert we just call it.
        """
        app = {}
        with unittest.mock.patch("beacon_api.app.init_db_pool") as db_mock:
            await initialize(app)
            db_mock.assert_called()


if __name__ == "__main__":
    unittest.main()
