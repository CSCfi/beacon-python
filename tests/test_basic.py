# import unittest
import asynctest
import asyncpg
from beacon_api.utils.db_load import parse_arguments
# from beacon_api.conf.config import init_db_pool


class MagicMockContext(asynctest.MagicMock):
    """Something."""

    async def __aenter__(self):
        """Do magic."""
        return self.aenter

    async def __aexit__(self, *args):
        """Do magic."""
        pass


async def create_db_mock():
    """Mock the db connection pool."""
    return asynctest.CoroutineMock(side_effect=asyncpg.pool.Pool)
    # return asynctest.CoroutineMock(asyncpg.create_pool())
    # return mock.__aenter__.return_value


class TestBasicFunctions(asynctest.TestCase):
    """Test supporting functions."""

    def test_parser(self):
        """Test argument parsing."""
        parsed = parse_arguments(['/path/to/datafile.csv', '/path/to/metadata.json'])
        self.assertEqual(parsed.datafile, '/path/to/datafile.csv')
        self.assertEqual(parsed.metadata, '/path/to/metadata.json')

    # @asynctest.mock.patch('beacon_api.conf.config.asyncpg', new_callable=MagicMockContext)
    # async def test_connection(self, db_mock):
    #     """Test database URL fetching."""
    #     # with asynctest.mock.patch('beacon_api.conf.config.asyncpg', side_effect=create_db_mock):
    #     db_mock.return_value.aenter.create_pool = asynctest.CoroutineMock(side_effect=asyncpg.pool.Pool)
    #     await init_db_pool()
    #     db_mock.assert_called()


if __name__ == '__main__':
    asynctest.main()
