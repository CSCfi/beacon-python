import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from beacon_api.app import init, main, initialize
from unittest import mock
import asyncpg
import asynctest
import json
import jwt
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from test.support import EnvironmentVarGuard


PARAMS = {'assemblyId': 'GRCh38',
          'referenceName': '1',
          'start': 10000,
          'referenceBases': 'A',
          'alternateBases': 'T'}


def generate_token(issuer):
    """Mock ELIXIR AAI token."""
    private_key = rsa.generate_private_key(public_exponent=65537,
                                           key_size=2048, backend=default_backend())
    pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                    format=serialization.PrivateFormat.PKCS8,
                                    encryption_algorithm=serialization.NoEncryption())
    token = jwt.encode({'iss': issuer, 'sub': 'smth@elixir-europe.org'},
                       pem, algorithm='RS256')

    public_key = private_key.public_key()
    pem_pub = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return token, pem_pub


async def create_db_mock(app):
    """Mock the db connection pool."""
    app['pool'] = asynctest.mock.Mock(asyncpg.create_pool())
    return app


async def mock_parse_request_object(request):
    """Mock parse request object."""
    return 'GET', json.dumps(PARAMS)


class AppTestCase(AioHTTPTestCase):
    """Test for Web app.

    Testing web app endpoints.
    """

    async def get_application(self):
        """Retrieve web Application for test."""
        token, public_key = generate_token('https://login.elixir-czech.org/oidc/')
        self.env = EnvironmentVarGuard()
        self.env.set('PUBLIC_KEY', str(public_key.decode('utf-8')))
        self.env.set('TOKEN', token.decode('utf-8'))
        with asynctest.mock.patch('beacon_api.app.initialize', side_effect=create_db_mock):
            return init()

    def tearDown(self):
        """Finish up tests."""
        self.env.unset('PUBLIC_KEY')
        self.env.unset('TOKEN')

    @unittest_run_loop
    async def test_info(self):
        """Test the info endpoint.

        The status should always be 200.
        """
        with asynctest.mock.patch('beacon_api.app.beacon_info', side_effect={"smth": "value"}):
            resp = await self.client.request("GET", "/")
        assert 200 == resp.status

    @unittest_run_loop
    async def test_post_info(self):
        """Test the info endpoint with POST.

        The status should always be 405.
        """
        resp = await self.client.request("POST", "/")
        assert 405 == resp.status

    @unittest_run_loop
    async def test_empty_get_query(self):
        """Test empty GET query endpoint."""
        resp = await self.client.request("GET", "/query")
        assert 400 == resp.status

    @unittest_run_loop
    async def test_empty_post_query(self):
        """Test empty POST query endpoint."""
        resp = await self.client.request("POST", "/query", data=json.dumps({}))
        assert 400 == resp.status

    @unittest_run_loop
    async def test_unauthorized_no_token_post_query(self):
        """Test unauthorized POST query endpoint, with no token."""
        resp = await self.client.request("POST", "/query",
                                         data=json.dumps(PARAMS),
                                         headers={'Authorization': "Bearer"})
        assert 401 == resp.status

    @unittest_run_loop
    async def test_unauthorized_token_post_query(self):
        """Test unauthorized POST query endpoint, bad token."""
        resp = await self.client.request("POST", "/query",
                                         data=json.dumps(PARAMS),
                                         headers={'Authorization': "Bearer x"})
        assert 401 == resp.status

    @unittest_run_loop
    async def test_invalid_scheme_get_query(self):
        """Test unauthorized GET query endpoint, invalid scheme."""
        params = '?assemblyId=GRCh38&referenceName=1&start=10000&referenceBases=A&alternateBases=T&datasetIds=dataset1'
        resp = await self.client.request("GET", f"/query{params}",
                                         headers={'Authorization': "SMTH x"})
        assert 401 == resp.status

    @asynctest.mock.patch('beacon_api.app.parse_request_object', side_effect=mock_parse_request_object)
    @asynctest.mock.patch('beacon_api.app.query_request_handler', side_effect=json.dumps(PARAMS))
    @unittest_run_loop
    async def test_valid_token_get_query(self, mock_handler, mock_object):
        """Test valid token GET query endpoint, invalid scheme."""
        token = os.environ.get('TOKEN')
        resp = await self.client.request("POST", "/query",
                                         data=json.dumps(PARAMS),
                                         headers={'Authorization': f"Bearer {token}"})
        assert 200 == resp.status

    @unittest_run_loop
    async def test_bad_json_post_query(self):
        """Test bad json POST query endpoint."""
        resp = await self.client.request("POST", "/query", data="")
        assert 500 == resp.status

    @asynctest.mock.patch('beacon_api.app.parse_request_object', side_effect=mock_parse_request_object)
    @asynctest.mock.patch('beacon_api.app.query_request_handler', side_effect=json.dumps(PARAMS))
    @unittest_run_loop
    async def test_valid_get_query(self, mock_handler, mock_object):
        """Test valid GET query endpoint."""
        params = '?assemblyId=GRCh38&referenceName=1&start=10000&referenceBases=A&alternateBases=T'
        with asynctest.mock.patch('beacon_api.app.initialize', side_effect=create_db_mock):
            resp = await self.client.request("GET", f"/query{params}")
        print(resp.text)
        print(dir(resp))
        assert 200 == resp.status

    @asynctest.mock.patch('beacon_api.app.parse_request_object', side_effect=mock_parse_request_object)
    @asynctest.mock.patch('beacon_api.app.query_request_handler', side_effect=json.dumps(PARAMS))
    @unittest_run_loop
    async def test_valid_post_query(self, mock_handler, mock_object):
        """Test valid POST query endpoint."""
        resp = await self.client.request("POST", "/query", data=json.dumps(PARAMS))
        assert 200 == resp.status


class AppTestCaseForbidden(AioHTTPTestCase):
    """Test for Web app 403.

    Testing web app for wrong issuer.
    """

    async def get_application(self):
        """Retrieve web Application for test."""
        token, public_key = generate_token('something')
        self.env = EnvironmentVarGuard()
        self.env.set('PUBLIC_KEY', str(public_key.decode('utf-8')))
        self.env.set('TOKEN', token.decode('utf-8'))
        with asynctest.mock.patch('beacon_api.app.initialize', side_effect=create_db_mock):
            return init()

    def tearDown(self):
        """Finish up tests."""
        self.env.unset('PUBLIC_KEY')
        self.env.unset('TOKEN')

    @asynctest.mock.patch('beacon_api.app.parse_request_object', side_effect=mock_parse_request_object)
    @asynctest.mock.patch('beacon_api.app.query_request_handler', side_effect=json.dumps(PARAMS))
    @unittest_run_loop
    async def test_forbidden_token_get_query(self, mock_handler, mock_object):
        """Test forbidden GET query endpoint, invalid scheme."""
        token = os.environ.get('TOKEN')
        resp = await self.client.request("POST", "/query",
                                         data=json.dumps(PARAMS),
                                         headers={'Authorization': f"Bearer {token}"})
        assert 403 == resp.status


class TestBasicFunctionsApp(asynctest.TestCase):
    """Test App Base.

    Testing basic functions from web app.
    """

    def setUp(self):
        """Initialise fixtures."""
        pass

    def tearDown(self):
        """Remove setup variables."""
        pass

    @mock.patch('beacon_api.app.web')
    def test_main(self, mock_webapp):
        """Should start the webapp."""
        main()
        mock_webapp.run_app.assert_called()

    def test_init(self):
        """Test init type."""
        server = init()
        self.assertIs(type(server), web.Application)

    async def test_initialize(self):
        """Test create db pool, should just return the result of init_db_pool.

        We will mock the init_db_pool, thus we assert we just call it.
        """
        app = {}
        with asynctest.mock.patch('beacon_api.app.init_db_pool') as db_mock:
            await initialize(app)
            db_mock.assert_called()


if __name__ == '__main__':
    unittest.main()
