import asynctest
from beacon_api.utils.db_load import parse_arguments
from beacon_api.conf.config import init_db_pool


class TestBasicFunctions(asynctest.TestCase):
    """Test supporting functions."""

    def test_parser(self):
        """Test argument parsing."""
        parsed = parse_arguments(['/path/to/datafile.csv', '/path/to/metadata.json'])
        self.assertEqual(parsed.datafile, '/path/to/datafile.csv')
        self.assertEqual(parsed.metadata, '/path/to/metadata.json')

    @asynctest.mock.patch('beacon_api.conf.config.asyncpg')
    async def test_connection(self, db_mock):
        """Test database URL fetching."""
        db_mock.return_value = asynctest.CoroutineMock(name='create_pool')
        db_mock.create_pool = asynctest.CoroutineMock()
        await init_db_pool()
        db_mock.create_pool.assert_called()


if __name__ == '__main__':
    asynctest.main()
