import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from beacon_api.app import init, main, create_db_pool
from unittest import mock
import asyncpg
import asynctest


async def create_db_mock(app):
    """Mock the db connection pool."""
    app['pool'] = asynctest.mock.Mock(asyncpg.create_pool())
    return app


class AppTestCase(AioHTTPTestCase):
    """Test for Web app.

    Testing web app endpoints.
    """

    async def get_application(self):
        """Retrieve web Application for test."""
        # app.on_startup.append(mock)
        with asynctest.mock.patch('beacon_api.app.create_db_pool', side_effect=create_db_mock):
            return init()

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

    async def test_create_db_pool(self):
        """Test create db pool, should just return the result of init_db_pool.

        We will mock the init_db_pool, thus we assert we just call it.
        """
        app = {}
        with asynctest.mock.patch('beacon_api.app.init_db_pool') as db_mock:
            await create_db_pool(app)
            db_mock.assert_called()


if __name__ == '__main__':
    unittest.main()
