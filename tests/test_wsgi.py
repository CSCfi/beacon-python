import unittest
# import testing.postgresql

from beacon_api.conf.config import application, db

TEST_DB = 'test.db'


class TestSearchAPI(unittest.TestCase):
    """Test beacon-search API functions and endpoints."""

    def setUp(self):
        """Execute this method on start."""
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False
        application.config['DEBUG'] = False
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + TEST_DB
        self.app = application.test_client()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        """Execute this method after each test."""
        db.drop_all()

    def test_get_response_code(self):
        """Test basic get."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
