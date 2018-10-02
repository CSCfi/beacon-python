import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from beacon_api.app import init, main
from unittest import mock


class AppTestCase(AioHTTPTestCase):
    """Test for Web app.

    Testing web app endpoints.
    """

    async def get_application(self):
        """Retrieve web Application for test."""
        return init()

    @unittest_run_loop
    async def test_info(self):
        """Simplest test the health endpoint."""
        resp = await self.client.request("GET", "/")
        assert 200 == resp.status
        # assert 'OK' == await resp.text()


class TestBasicFunctionsApp(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
