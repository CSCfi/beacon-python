import unittest
import asynctest

# import asyncpg

from beacon_api.utils.db_load import BeaconDB


class DatabaseTestCase(asynctest.TestCase):
    """Test database operations."""

    def setUp(self):
        """Initialise BeaconDB object."""
        self._db_url = 'http://url.fi'
        self._db = BeaconDB(self._db_url)

    def tearDown(self):
        """Close database connection after tests."""
        pass

    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg')
    async def test_connection(self, db_mock):
        """Test database URL fetching."""
        await self._db.connection()
        db_mock.connect.assert_called_with(self._db_url)

    # @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg')
    # async def test_check_tables(self, db_mock):
    #     """Test checking tables."""
    #     # self._db._conn = asynctest.CoroutineMock(side_effect=asyncpg.connect())
    #     db_mock.return_value = asynctest.CoroutineMock(name='connect')
    #     db_mock.connect = asynctest.CoroutineMock()
    #     await self._db.connection()
    #     db_mock.connect.assert_called_with(self._db_url)
    #     db_mock.connect.side_effect = asynctest.CoroutineMock(name='fetch')
    #     db_mock.connect.fetch.side_effect = asynctest.CoroutineMock()
    #     await self._db.check_tables(['DATATSET1'])
    #     db_mock.connect.fetch.assert_called()

    def test_bad_init(self):
        """Capture error in case of anything wrong with initializing BeaconDB."""
        with self.assertRaises(TypeError):
            BeaconDB()


if __name__ == '__main__':
    unittest.main()
