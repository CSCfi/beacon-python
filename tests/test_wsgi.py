import unittest

# from unittest import mock

from beacon_api.conf.config import application


class TestSearchAPI(unittest.TestCase):
    """Test beacon-search API functions and endpoints."""

    def setUp(self):
        """Execute this method on start."""
        # app.config['TESTING'] = True
        # app.config['WTF_CSRF_ENABLED'] = False
        # app.config['DEBUG'] = False
        self.app = application.test_client()

    def tearDown(self):
        """Execute this method after each test."""
        pass

    def test_get_response_code(self):
        """Test basic get."""
        response = self.app.get('/', follow_redirects=True)
        print(response)
        self.assertEqual(response.status_code, 200)
