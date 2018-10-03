import unittest
# import asyncio

from unittest import mock

from beacon_api.utils.db_load import BeaconDB, parse_arguments


class DatabaseTestCase(unittest.TestCase):
    """Test database operations."""

    def setUp(self):
        """Initialise BeaconDB object."""
        self._db_url = 'http://url.fi'
        self._db = BeaconDB(self._db_url)

    def tearDown(self):
        """Close database connection after tests."""
        pass

    @mock.patch('beacon_api.utils.db_load.asyncpg')
    async def test_connection(self, db_mock):
        """Test database URL fetching."""
        # db_mock.return_value = mock.MagicMock()
        # asyncio.get_event_loop().run_until_complete(self._db.connection())
        await self._db.connection()
        db_mock.connect.assert_called()

    def test_bad_init(self):
        with self.assertRaises(TypeError):
            BeaconDB()


class TestBasicFunctions(unittest.TestCase):
    """Test supporting functions."""

    def setUp(self):
        """Initialise fixtures."""
        pass

    def tearDown(self):
        """Remove setup variables."""
        pass

    def test_parser(self):
        """Test argument parsing."""
        parsed = parse_arguments(['/path/to/datafile.csv', '/path/to/metadata.json'])
        self.assertEqual(parsed.datafile, '/path/to/datafile.csv')
        self.assertEqual(parsed.metadata, '/path/to/metadata.json')


if __name__ == '__main__':
    unittest.main()
